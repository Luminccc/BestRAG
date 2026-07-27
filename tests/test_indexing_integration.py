"""Indexing Integration Test — 验证 Indexing 域 PDR v1.0 验收标准。

运行方式::

    uv run pytest tests/test_indexing_integration.py -v

注意：TC-002/TC-003/TC-004 需要 Embedding 和 VectorStore Provider 可用，
默认使用 mock 避免依赖真实服务和模型。
"""

from unittest.mock import patch

import pytest

from core.config import ConfigManager, IndexingConfig
from core.registry import ServiceRegistry
from indexing.model import IndexChunk, IndexResult
from indexing.writer import VectorWriter
from indexing.pipeline import IndexPipeline
from indexing.service import IndexingService


# ═══════════════════════════════════════════════════
# Fixtures（每次测试前清空状态）
# ═══════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _reset():
    ConfigManager().reset()
    ServiceRegistry().clear()
    yield
    ConfigManager().reset()
    ServiceRegistry().clear()


@pytest.fixture
def sample_chunks():
    """创建模拟 Chunk 列表（结构对齐 processor.chunker.model.Chunk）。"""
    from unittest.mock import MagicMock
    c1 = MagicMock()
    c1.id = "c-1"
    c1.document_id = "doc-1"
    c1.content = "BestRAG 是一个轻量级 RAG 框架。"
    c1.index = 0
    c1.metadata = {}

    c2 = MagicMock()
    c2.id = "c-2"
    c2.document_id = "doc-1"
    c2.content = "它基于 DDD 架构设计。"
    c2.index = 1
    c2.metadata = {}

    c3 = MagicMock()
    c3.id = "c-3"
    c3.document_id = "doc-1"
    c3.content = "支持多种文档格式。"
    c3.index = 2
    c3.metadata = {}

    return [c1, c2, c3]


@pytest.fixture
def processed_document(sample_chunks):
    """创建模拟 ProcessedDocument。"""
    from unittest.mock import MagicMock
    doc = MagicMock()
    doc.id = "doc-1"
    doc.content = "test"
    doc.metadata = MagicMock()

    pd = MagicMock()
    pd.document = doc
    pd.chunks = sample_chunks
    return pd


# ═══════════════════════════════════════════════════
# TC-001: Chunk 转换
# ═══════════════════════════════════════════════════

def test_chunk_to_index_chunk_conversion(processed_document):
    """Chunk → IndexChunk 转换：保留 id、content，填充 document_id metadata。"""
    pipeline = IndexPipeline()
    index_chunks = pipeline._to_index_chunks(processed_document)

    assert len(index_chunks) == 3
    assert all(isinstance(c, IndexChunk) for c in index_chunks)
    assert all(c.document_id == "doc-1" for c in index_chunks)
    assert all("document_id" in c.metadata for c in index_chunks)
    assert all("chunk_index" in c.metadata for c in index_chunks)

    # embedding 尚未填充
    assert all(c.embedding is None for c in index_chunks)


def test_empty_chunks():
    """空 chunk 列表 → 空 IndexChunk 列表。"""
    from unittest.mock import MagicMock
    doc = MagicMock()
    doc.id = "doc-1"
    doc.content = "test"
    doc.metadata = MagicMock()
    pd = MagicMock()
    pd.document = doc
    pd.chunks = []

    pipeline = IndexPipeline()
    result = pipeline.execute(pd)

    assert result.success
    assert result.chunk_count == 0


# ═══════════════════════════════════════════════════
# TC-002: Embedding 调用
# ═══════════════════════════════════════════════════

def test_embedding_call_batch():
    """Embedding 批量调用：输入 N 个文本，输出 N 个向量（mock 验证）。"""
    cfg = ConfigManager().get()
    cfg.indexing.batch_size = 2  # 小 batch 验证分批逻辑

    # 模拟 Embedding Provider
    class _MockEmbedding:
        def embed_documents(self, texts):
            return [[0.1] * 1024 for _ in texts]

    reg = ServiceRegistry()
    reg.register("embedding", _MockEmbedding())

    chunks = [
        IndexChunk(id="c-1", document_id="doc-1", content="text1", metadata={}),
        IndexChunk(id="c-2", document_id="doc-1", content="text2", metadata={}),
        IndexChunk(id="c-3", document_id="doc-1", content="text3", metadata={}),
    ]

    pipeline = IndexPipeline()
    pipeline._embed_chunks(chunks)

    # 3 个 chunk 全部获得 embedding
    assert all(c.embedding is not None for c in chunks)
    assert all(len(c.embedding) == 1024 for c in chunks)  # type: ignore


# ═══════════════════════════════════════════════════
# TC-003: Vector 写入
# ═══════════════════════════════════════════════════

def test_vector_writer_calls_add():
    """VectorWriter 将 IndexChunk 转为 vectorstore.add() 调用（mock 验证）。"""
    class _MockVectorStore:
        def add(self, vectors, texts, metadatas, ids):
            assert len(vectors) == 2
            assert texts == ["Hello", "World"]
            return ids

    reg = ServiceRegistry()
    mock_store = _MockVectorStore()
    reg.register("vector_store", mock_store)

    chunks = [
        IndexChunk(id="c-1", document_id="doc-1", content="Hello", metadata={}, embedding=[0.1] * 1024),
        IndexChunk(id="c-2", document_id="doc-1", content="World", metadata={}, embedding=[0.2] * 1024),
    ]

    writer = VectorWriter()
    ids = writer.write(chunks)

    assert ids == ["c-1", "c-2"]


def test_vector_writer_skips_unembedded():
    """缺少 embedding 的 chunk 被跳过。"""
    class _MockVectorStore:
        def add(self, vectors, texts, metadatas, ids):
            return ids

    ServiceRegistry().register("vector_store", _MockVectorStore())

    chunks = [
        IndexChunk(id="c-1", document_id="doc-1", content="text", metadata={}, embedding=None),
    ]
    writer = VectorWriter()
    ids = writer.write(chunks)
    assert ids == []


# ═══════════════════════════════════════════════════
# TC-004: 完整 Index Pipeline
# ═══════════════════════════════════════════════════

def test_full_index_pipeline(processed_document):
    """完整 Pipeline：ProcessedDocument → IndexResult.success=True。"""
    # 注册 mock Provider
    class _MockEmbedding:
        def embed_documents(self, texts):
            return [[0.1] * 1024 for _ in texts]

    class _MockVectorStore:
        def add(self, vectors, texts, metadatas, ids):
            return ids

    reg = ServiceRegistry()
    reg.register("embedding", _MockEmbedding())
    reg.register("vector_store", _MockVectorStore())

    pipeline = IndexPipeline()
    result = pipeline.execute(processed_document)

    assert result.success
    assert result.document_id == "doc-1"
    assert result.chunk_count == 3
    assert result.error is None


def test_service_layer(processed_document):
    """IndexingService.index() 封装 Pipeline 调用。"""
    class _MockEmbedding:
        def embed_documents(self, texts):
            return [[0.1] * 1024 for _ in texts]

    class _MockVectorStore:
        def add(self, vectors, texts, metadatas, ids):
            return ids

    ServiceRegistry().register("embedding", _MockEmbedding())
    ServiceRegistry().register("vector_store", _MockVectorStore())

    svc = IndexingService()
    result = svc.index(processed_document)

    assert result.success
    assert result.chunk_count == 3


# ═══════════════════════════════════════════════════
# TC-005: IndexingConfig
# ═══════════════════════════════════════════════════

def test_indexing_config_defaults():
    """IndexingConfig 默认值 batch_size=32, auto_commit=True。"""
    cfg = ConfigManager().get()
    assert cfg.indexing.batch_size == 32
    assert cfg.indexing.auto_commit is True
