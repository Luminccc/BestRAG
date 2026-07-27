"""Retrieval Enhancement V2 Integration Test — 验证检索增强域 PDR v1.0 验收标准。

运行方式::

    uv run pytest tests/test_retrieval_v2_integration.py -v

TC-001 Hybrid Retrieval      TC-004 Retrieval Cache
TC-002 Metadata Filter       TC-005 Cache Invalidation
TC-003 Embedding Cache       TC-006 Redis Cache Integration
"""

import time
from unittest.mock import MagicMock, patch

import pytest
import redis

from core.config import ConfigManager, CoreConfig, RetrievalConfig
from core.registry import ServiceRegistry
from retrieval.cache.embedding_cache import EmbeddingCache
from retrieval.cache.retrieval_cache import RetrievalCache
from retrieval.filter.metadata import MetadataFilter
from retrieval.fusion.weighted import WeightedFusion
from retrieval.retriever.bm25 import BM25Retriever, clear_corpus, register_corpus
from retrieval.retriever.hybrid import HybridRetriever
from retrieval.retriever.model import RetrievalResult
from retrieval.retriever.vector import VectorRetriever
from retrieval.pipeline import RetrievalPipelineV2


# ═══════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _reset():
    ConfigManager().reset()
    ServiceRegistry().clear()
    clear_corpus()
    yield
    ConfigManager().reset()
    ServiceRegistry().clear()
    clear_corpus()


@pytest.fixture
def mock_embedding():
    """模拟 Embedding Provider：返回 4 维向量。"""
    class _Emb:
        def embed_text(self, text):
            return MagicMock(vector=[0.1] * 4)
        def embed_documents(self, texts):
            return [[0.1] * 4 for _ in texts]
    return _Emb()


@pytest.fixture
def mock_vector_store():
    """模拟 VectorStore Provider。"""
    class _VS:
        def search(self, query_vector, top_k, filters=None):
            return [
                ("v-1", 0.95, "向量结果1：RAG框架部署指南", {"dept": "tech"}),
                ("v-2", 0.80, "向量结果2：财务系统", {"dept": "finance"}),
                ("v-3", 0.60, "向量结果3：通用文档", {"dept": "tech"}),
            ]
        def add(self, vectors, texts, metadatas, ids):
            return ids
    return _VS()


@pytest.fixture
def bm25_corpus():
    """预填充 BM25 corpus。"""
    register_corpus([
        {"chunk_id": "b-1", "content": "RAG框架的部署需要向量数据库和Embedding模型", "metadata": {"dept": "tech"}},
        {"chunk_id": "b-2", "content": "财务系统报销流程说明", "metadata": {"dept": "finance"}},
        {"chunk_id": "b-3", "content": "企业知识库架构设计文档关于RAG的最佳实践", "metadata": {"dept": "tech"}},
    ])


@pytest.fixture
def redis_client():
    """真实 Redis 连接（TC-006）。"""
    try:
        r = redis.Redis(host="127.0.0.1", port=6379, db=0, protocol=2, decode_responses=True)
        r.ping()
        return r
    except redis.RedisError:
        pytest.skip("Redis not available")


# ═══════════════════════════════════════════════════
# TC-001: Hybrid Retrieval
# ═══════════════════════════════════════════════════

def test_vector_retriever(mock_embedding, mock_vector_store):
    """VectorRetriever 通过 Registry 调用 embedding + vectorstore。"""
    ServiceRegistry().register("embedding", mock_embedding)
    ServiceRegistry().register("vector_store", mock_vector_store)

    retriever = VectorRetriever()
    results = retriever.retrieve("部署指南", top_k=3)

    assert len(results) == 3
    assert results[0].chunk_id == "v-1"
    assert results[0].score == 0.95


def test_bm25_retriever(bm25_corpus):
    """BM25Retriever 对已注册 corpus 进行关键词检索。"""
    retriever = BM25Retriever()
    results = retriever.retrieve("RAG 部署", top_k=3)

    assert len(results) > 0
    assert all(isinstance(r, RetrievalResult) for r in results)


def test_hybrid_fusion(mock_embedding, mock_vector_store, bm25_corpus):
    """HybridRetriever 融合 Vector + BM25 结果。"""
    ServiceRegistry().register("embedding", mock_embedding)
    ServiceRegistry().register("vector_store", mock_vector_store)

    hybrid = HybridRetriever()
    results = hybrid.retrieve("RAG 部署", top_k=5)

    assert len(results) > 0
    # 融合结果应包含两方面：Vector 权重高所以 vector 结果靠前
    assert len(results) <= 5


# ═══════════════════════════════════════════════════
# TC-002: Metadata Filter
# ═══════════════════════════════════════════════════

def test_metadata_filter_passes_matching():
    """匹配条件的记录保留。"""
    results = [
        RetrievalResult(chunk_id="1", score=0.9, content="A", metadata={"dept": "finance"}),
        RetrievalResult(chunk_id="2", score=0.8, content="B", metadata={"dept": "tech"}),
    ]
    f = MetadataFilter()
    filtered = f.filter(results, {"dept": "finance"})
    assert len(filtered) == 1
    assert filtered[0].chunk_id == "1"


def test_metadata_filter_empty_conditions():
    """空条件原样返回。"""
    results = [RetrievalResult(chunk_id="1", score=0.9, content="A", metadata={})]
    f = MetadataFilter()
    assert f.filter(results, {}) == results


# ═══════════════════════════════════════════════════
# TC-003: Embedding Cache (mock Redis)
# ═══════════════════════════════════════════════════

def test_embedding_cache_hit_miss(redis_client):
    """第一次 MISS，第二次 HIT。"""
    # 配置 cache enabled
    cfg = ConfigManager().get()
    cfg.retrieval.cache_enabled = True

    cache = EmbeddingCache(client=redis_client)
    query = "测试查询"

    # 清空旧缓存
    cache.delete(query)

    # 第一次：MISS
    assert cache.get(query) is None

    # 写入缓存
    cache.set(query, [0.1, 0.2, 0.3])
    # 第二次：HIT
    vec = cache.get(query)
    assert vec == [0.1, 0.2, 0.3]


# ═══════════════════════════════════════════════════
# TC-004: Retrieval Cache (mock Redis)
# ═══════════════════════════════════════════════════

def test_retrieval_cache_hit_miss(redis_client):
    """相同 params 第二次 HIT。"""
    cfg = ConfigManager().get()
    cfg.retrieval.cache_enabled = True
    cfg.retrieval.index_version = "v_test"

    cache = RetrievalCache(client=redis_client)

    results = [RetrievalResult(chunk_id="c1", score=0.9, content="test", metadata={})]

    # 清理可能残留的旧缓存
    cache.delete("query", "hybrid", 10, None)

    # 第一次：MISS
    assert cache.get("query", "hybrid", 10, None) is None
    # 写入
    cache.set("query", "hybrid", 10, None, results)
    # 第二次 HIT
    cached = cache.get("query", "hybrid", 10, None)
    assert cached is not None
    assert len(cached) == 1
    assert cached[0].chunk_id == "c1"


# ═══════════════════════════════════════════════════
# TC-005: Cache Invalidation (index_version 变更)
# ═══════════════════════════════════════════════════

def test_cache_invalidation_by_index_version(redis_client):
    """index_version 变更后缓存 MISS。"""
    cfg = ConfigManager().get()
    cfg.retrieval.cache_enabled = True
    cfg.retrieval.index_version = "v1"

    cache1 = RetrievalCache(client=redis_client)
    results = [RetrievalResult(chunk_id="c1", score=0.9, content="test", metadata={})]
    cache1.set("query", "hybrid", 10, None, results)

    # v1 命中
    assert cache1.get("query", "hybrid", 10, None) is not None

    # 切换到 v2 → MISS
    cfg.retrieval.index_version = "v2"
    cache2 = RetrievalCache(client=redis_client)
    assert cache2.get("query", "hybrid", 10, None) is None


# ═══════════════════════════════════════════════════
# TC-006: Redis Cache Integration（真实 Redis）
# ═══════════════════════════════════════════════════

def test_redis_embedding_cache_integration(redis_client):
    """Redis SET → GET 端到端。"""
    cfg = ConfigManager().get()
    cfg.retrieval.cache_enabled = True

    cache = EmbeddingCache(client=redis_client)
    cache.delete("integration_test")

    # SET
    vec = [0.123, 0.456, 0.789]
    cache.set("integration_test", vec)
    # GET
    result = cache.get("integration_test")
    assert result == vec

    # TTL 存在
    key = cache._make_key("integration_test", "v1")
    ttl = redis_client.ttl(key)
    assert ttl > 0


def test_redis_retrieval_cache_integration(redis_client):
    """Redis 检索缓存 SET → GET 端到端。"""
    cfg = ConfigManager().get()
    cfg.retrieval.cache_enabled = True
    cfg.retrieval.index_version = "v_integration"

    cache = RetrievalCache(client=redis_client)

    results = [
        RetrievalResult(chunk_id="rc1", score=0.95, content="RAG 部署文档", metadata={"dept": "tech"}),
        RetrievalResult(chunk_id="rc2", score=0.88, content="向量数据库选型", metadata={"dept": "tech"}),
    ]
    cache.set("如何部署RAG", "hybrid", 5, {"dept": "tech"}, results)

    cached = cache.get("如何部署RAG", "hybrid", 5, {"dept": "tech"})
    assert cached is not None
    assert len(cached) == 2
    assert cached[0].score == 0.95
