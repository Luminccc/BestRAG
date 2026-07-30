"""Chunk Strategy 单元测试。

验证：
- BaseChunkStrategy 接口
- 现有 RecursiveChunkStrategy / FixedChunkStrategy 兼容性
- execute 委托给 split
"""

from datetime import datetime

import pytest

from core.strategy import BaseChunkStrategy
from document.model import Document, DocumentMetadata, DocumentType
from processor.chunker.service import ChunkService, CHUNK_STRATEGIES
from processor.chunker.strategy import RecursiveChunkStrategy, FixedChunkStrategy


class TestChunkStrategyInterface:
    """Chunk 策略接口测试。"""

    def test_base_chunk_strategy_is_abstract(self):
        """BaseChunkStrategy 不能直接实例化。"""
        with pytest.raises(TypeError):
            BaseChunkStrategy()  # type: ignore

    def test_recursive_has_name(self):
        """RecursiveChunkStrategy 有 name 属性。"""
        s = RecursiveChunkStrategy()
        assert s.name == "recursive"

    def test_fixed_has_name(self):
        """FixedChunkStrategy 有 name 属性。"""
        s = FixedChunkStrategy()
        assert s.name == "fixed"

    def test_execute_delegates_to_split(self):
        """execute 委托给 split，结果一致。"""
        s = FixedChunkStrategy()
        text = "Hello world. This is a test."
        r1 = s.split(text, "doc1")
        r2 = s.execute(text, "doc1")
        assert len(r1) == len(r2)
        assert r1[0].content == r2[0].content

    def test_split_returns_chunk_list(self):
        """split 返回 Chunk 列表。"""
        s = RecursiveChunkStrategy()
        text = "This is a test document.\n\nIt has multiple paragraphs.\n\nThis is the third one."
        chunks = s.split(text, "doc1")
        assert len(chunks) > 0
        assert all(c.document_id == "doc1" for c in chunks)


class TestChunkService:
    """ChunkService 兼容性测试。"""

    @pytest.fixture
    def doc(self):
        meta = DocumentMetadata(filename="test.txt", file_type=DocumentType.TXT)
        return Document(content="Hello world. This is a test document.", metadata=meta)

    def test_chunk_fixed_strategy(self, doc):
        """chunk 使用 fixed 策略。"""
        svc = ChunkService()
        chunks = svc.chunk(doc, "fixed")
        assert len(chunks) > 0

    def test_chunk_recursive_strategy(self, doc):
        """chunk 使用 recursive 策略。"""
        svc = ChunkService()
        chunks = svc.chunk(doc, "recursive")
        assert len(chunks) > 0

    def test_chunk_invalid_strategy(self, doc):
        """使用未知策略应抛出 ValueError。"""
        svc = ChunkService()
        with pytest.raises(ValueError, match="未知策略"):
            svc.chunk(doc, "non_existent")

    def test_chunk_returns_chunks_with_document_id(self, doc):
        """返回的 Chunk 包含正确的 document_id。"""
        svc = ChunkService()
        chunks = svc.chunk(doc, "recursive")
        for c in chunks:
            assert c.document_id == doc.id

    def test_registry_auto_register(self):
        """ChunkService 自动注册策略到 Registry。"""
        from core.registry import get_registry
        svc = ChunkService()
        # 触发注册
        svc._ensure_registry()
        registry = get_registry()
        assert registry.strategy.has("chunk:recursive")
        assert registry.strategy.has("chunk:fixed")
