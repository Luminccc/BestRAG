"""BestRAG v0.3 Phase 5 测试 — Cache & Runtime Acceleration Framework。

覆盖：
1. Core 测试     — CacheKey / MemoryCacheProvider / CacheManager
2. Cache 类型测试 — QueryCache / EmbeddingCache / RetrievalCache
3. Trace 测试    — CacheTrace
4. Metrics 测试  — CacheMetrics
5. Service 测试  — CacheService
6. Optimizer 测试 — CacheOptimizer
7. Config 测试   — CacheConfigV3
8. 集成测试      — 完整缓存流程

运行::

    uv run pytest tests/core/v03/cache/test_phase5.py -v
"""

import time
import pytest

from cache import (
    CacheKey, CacheManager, MemoryCacheProvider,
    QueryCache, EmbeddingCache, RetrievalCache,
)
from cache.core.trace import CacheTrace
from cache.core.metrics import CacheMetrics
from cache.core.optimizer import CacheOptimizer
from cache.service import CacheService
from core.config_models.cache_v3 import CacheConfigV3, CacheProviderConfig, CacheTypeConfig
from core.config import CoreConfig
from core.models.trace import Trace, TraceType


# ═══════════════════════════════════════════════════
# Test 1: Core 测试
# ═══════════════════════════════════════════════════

class TestCacheKey:
    def test_make_key(self):
        key = CacheKey.make("query", query="hello", profile="default")
        assert key.startswith("bestrag:query:")
        assert len(key) > 20

    def test_make_key_different_params(self):
        k1 = CacheKey.make("query", query="hello", top_k=5)
        k2 = CacheKey.make("query", query="hello", top_k=10)
        assert k1 != k2

    def test_make_key_same_params(self):
        k1 = CacheKey.make("query", query="hello", top_k=5)
        k2 = CacheKey.make("query", query="hello", top_k=5)
        assert k1 == k2  # 幂等

    def test_from_dict(self):
        key = CacheKey.from_dict("embedding", {"text": "hello", "model": "bge"})
        assert key.startswith("bestrag:embedding:")


class TestMemoryCacheProvider:
    def test_set_and_get(self):
        p = MemoryCacheProvider()
        p.set("k", "v")
        assert p.get("k") == "v"

    def test_get_not_found(self):
        p = MemoryCacheProvider()
        assert p.get("nonexistent") is None

    def test_delete(self):
        p = MemoryCacheProvider()
        p.set("k", "v")
        assert p.delete("k") is True
        assert p.get("k") is None
        assert p.delete("k") is False

    def test_exists(self):
        p = MemoryCacheProvider()
        p.set("k", "v")
        assert p.exists("k") is True
        assert p.exists("x") is False

    def test_clear(self):
        p = MemoryCacheProvider()
        p.set("a", 1)
        p.set("b", 2)
        p.clear()
        assert p.size() == 0

    def test_ttl_expiry(self):
        p = MemoryCacheProvider()
        p.set("k", "v", ttl=1)
        assert p.get("k") == "v"
        time.sleep(1.1)
        assert p.get("k") is None

    def test_eviction(self):
        p = MemoryCacheProvider(max_size=2)
        p.set("a", 1)
        p.set("b", 2)
        p.set("c", 3)  # 应淘汰 a
        assert p.get("a") is None
        assert p.get("b") == 2
        assert p.get("c") == 3


class TestCacheManager:
    def test_single_provider(self):
        p = MemoryCacheProvider()
        mgr = CacheManager(providers=[p])
        mgr.set("k", "v")
        assert mgr.get("k") == "v"

    def test_multi_level(self):
        l1 = MemoryCacheProvider()
        l2 = MemoryCacheProvider()
        mgr = CacheManager(providers=[l1, l2])

        mgr.set("k", "v")
        assert l1.get("k") == "v"  # L1 和 L2 都有
        assert l2.get("k") == "v"

    def test_statistics(self):
        p = MemoryCacheProvider()
        mgr = CacheManager(providers=[p])

        mgr.get("miss_key")  # miss
        mgr.set("hit_key", "v")
        mgr.get("hit_key")  # hit
        mgr.get("hit_key")  # hit

        stats = mgr.get_stats()
        assert stats.hits == 2
        assert stats.misses == 1
        assert stats.hit_rate > 0

    def test_namespace_stats(self):
        p = MemoryCacheProvider()
        mgr = CacheManager(providers=[p])

        mgr.get("k1", namespace="ns1")  # miss
        mgr.set("k2", "v", namespace="ns2")
        mgr.get("k2", namespace="ns2")  # hit

        ns_stats = mgr.get_namespace_stats()
        assert ns_stats["ns1"]["misses"] == 1
        assert ns_stats["ns2"]["hits"] == 1


# ═══════════════════════════════════════════════════
# Test 2: Cache 类型测试
# ═══════════════════════════════════════════════════

class TestQueryCache:
    def test_set_and_get(self):
        mgr = CacheManager(providers=[MemoryCacheProvider()])
        qc = QueryCache(manager=mgr)
        qc.set("test query", ["result1", "result2"])
        results = qc.get("test query")
        assert results == ["result1", "result2"]

    def test_miss(self):
        qc = QueryCache()
        assert qc.get("unknown query") is None

    def test_profile_isolation(self):
        """不同 Profile 不共享缓存。"""
        mgr = CacheManager(providers=[MemoryCacheProvider()])
        qc = QueryCache(manager=mgr)
        qc.set("query", "profile_a_result", profile="a")
        assert qc.get("query", profile="b") is None
        assert qc.get("query", profile="a") == "profile_a_result"

    def test_delete(self):
        mgr = CacheManager(providers=[MemoryCacheProvider()])
        qc = QueryCache(manager=mgr)
        qc.set("q", "v")
        qc.delete("q")
        assert qc.get("q") is None


class TestEmbeddingCache:
    def test_set_and_get(self):
        mgr = CacheManager(providers=[MemoryCacheProvider()])
        ec = EmbeddingCache(manager=mgr)
        ec.set("hello", [0.1, 0.2, 0.3])
        vec = ec.get("hello")
        assert vec == [0.1, 0.2, 0.3]

    def test_model_isolation(self):
        """不同模型不共享缓存。"""
        mgr = CacheManager(providers=[MemoryCacheProvider()])
        ec = EmbeddingCache(manager=mgr)
        ec.set("text", [1.0], model="bge")
        assert ec.get("text", model="other") is None


class TestRetrievalCache:
    def test_set_and_get(self):
        mgr = CacheManager(providers=[MemoryCacheProvider()])
        rc = RetrievalCache(manager=mgr)
        rc.set("query", [{"id": "doc1"}], top_k=5)
        results = rc.get("query", top_k=5)
        assert results == [{"id": "doc1"}]

    def test_profile_isolation(self):
        mgr = CacheManager(providers=[MemoryCacheProvider()])
        rc = RetrievalCache(manager=mgr)
        rc.set("query", "profile_x", profile="x")
        assert rc.get("query", profile="y") is None


# ═══════════════════════════════════════════════════
# Test 3: CacheTrace 测试
# ═══════════════════════════════════════════════════

class TestCacheTrace:
    def test_record_lookup(self):
        ct = CacheTrace()
        ct.record_lookup("query_cache", "bestrag:query:abc")
        # 不应报错

    def test_record_hit(self):
        ct = CacheTrace()
        ct.record_hit("query_cache", "bestrag:query:abc", latency_ms=0.5)
        # 不应报错

    def test_record_miss(self):
        ct = CacheTrace()
        ct.record_miss("query_cache", "bestrag:query:abc")
        # 不应报错

    def test_record_refresh(self):
        ct = CacheTrace()
        ct.record_refresh("query_cache", "bestrag:query:abc", saved_ms=150)
        # 不应报错

    def test_record_expire(self):
        ct = CacheTrace()
        ct.record_expire("query_cache", "bestrag:query:abc")
        # 不应报错

    def test_with_trace_context(self):
        """集成 TraceContext 时记录事件到 Trace。"""
        from trace import TraceContext, DefaultTraceCollector
        from trace.storage import MemoryTraceStorage

        storage = MemoryTraceStorage()
        collector = DefaultTraceCollector(storage=storage)
        ctx = TraceContext(collector=collector)

        ctx.start_trace(TraceType.RETRIEVAL)
        ct = CacheTrace(trace_ctx=ctx)
        ct.record_hit("query_cache", "key123")
        ctx.end_trace()

        traces = storage.query()
        assert len(traces) >= 1


# ═══════════════════════════════════════════════════
# Test 4: CacheMetrics 测试
# ═══════════════════════════════════════════════════

class TestCacheMetrics:
    def test_empty_metrics(self):
        mgr = CacheManager(providers=[MemoryCacheProvider()])
        metrics = CacheMetrics(mgr)
        data = metrics.to_dict()
        assert data["hit_rate"] == 0
        assert data["total_hits"] == 0

    def test_with_data(self):
        p = MemoryCacheProvider()
        mgr = CacheManager(providers=[p])
        mgr.set("k", "v")
        mgr.get("k")  # hit
        mgr.get("x")  # miss

        metrics = CacheMetrics(mgr)
        assert metrics.get_hit_rate() > 0
        assert metrics.get_latency_saved(100) > 0

    def test_to_dict(self):
        mgr = CacheManager(providers=[MemoryCacheProvider()])
        metrics = CacheMetrics(mgr)
        d = metrics.to_dict()
        assert "hit_rate" in d
        assert "namespaces" in d


# ═══════════════════════════════════════════════════
# Test 5: CacheService 测试
# ═══════════════════════════════════════════════════

class TestCacheService:
    def test_get_statistics_empty(self):
        svc = CacheService()
        data = svc.get_statistics()
        assert data["total_hits"] == 0

    def test_get_statistics_with_data(self):
        p = MemoryCacheProvider()
        mgr = CacheManager(providers=[p])
        mgr.set("k", "v")
        mgr.get("k")

        svc = CacheService(manager=mgr)
        data = svc.get_statistics()
        assert data["total_hits"] == 1

    def test_get_dashboard_data(self):
        p = MemoryCacheProvider()
        mgr = CacheManager(providers=[p])
        svc = CacheService(manager=mgr)
        data = svc.get_dashboard_data()
        assert "summary" in data
        assert "namespaces" in data


# ═══════════════════════════════════════════════════
# Test 6: CacheOptimizer 测试
# ═══════════════════════════════════════════════════

class TestCacheOptimizer:
    def test_suggest_ttl_default(self):
        p = MemoryCacheProvider()
        mgr = CacheManager(providers=[p])
        opt = CacheOptimizer(mgr)
        result = opt.suggest_ttl("default", 3600)
        assert result["current_ttl"] == 3600
        assert result["namespace"] == "default"

    def test_suggest_ttl_high_hit_rate(self):
        p = MemoryCacheProvider()
        mgr = CacheManager(providers=[p])
        # 制造高命中率
        mgr.set("k", "v")
        for _ in range(10):
            mgr.get("k")
        mgr.get("miss_x")  # 只有一次 miss

        opt = CacheOptimizer(mgr)
        result = opt.suggest_ttl("default", 3600)
        # 高命中率应建议延长 TTL
        assert result["suggested_ttl"] >= 3600

    def test_get_optimization_report(self):
        p = MemoryCacheProvider()
        mgr = CacheManager(providers=[p])
        opt = CacheOptimizer(mgr)
        report = opt.get_optimization_report({"query": 3600, "embedding": 86400})
        assert len(report) == 2


# ═══════════════════════════════════════════════════
# Test 7: Config 测试
# ═══════════════════════════════════════════════════

def test_cache_config_v3_defaults():
    cfg = CacheConfigV3()
    assert cfg.enabled is True
    assert cfg.provider.type == "memory"
    assert cfg.query_cache.ttl == 3600
    assert cfg.embedding_cache.ttl == 86400
    assert cfg.retrieval_cache.ttl == 3600


def test_core_config_has_cache_v3():
    cfg = CoreConfig()
    assert hasattr(cfg, "cache_v3")
    assert cfg.cache_v3.enabled is True
    assert cfg.cache_v3.provider.type == "memory"


# ═══════════════════════════════════════════════════
# Test 8: 端到端集成测试
# ═══════════════════════════════════════════════════

def test_end_to_end_cache_flow():
    """完整流程：Provider -> Manager -> CacheType -> Statistics。"""
    # 1. 创建 Provider 和 Manager
    provider = MemoryCacheProvider()
    manager = CacheManager(providers=[provider])

    # 2. 使用 QueryCache
    qc = QueryCache(manager=manager)
    qc.set("What is RAG?", ["doc1", "doc2"], profile="default")
    assert qc.get("What is RAG?") == ["doc1", "doc2"]

    # 3. 使用 EmbeddingCache
    ec = EmbeddingCache(manager=manager)
    ec.set("hello world", [0.1, 0.2, 0.3], model="bge-m3")
    assert ec.get("hello world", model="bge-m3") == [0.1, 0.2, 0.3]

    # 4. 使用 RetrievalCache
    rc = RetrievalCache(manager=manager)
    rc.set("test query", ["result"], top_k=10, profile="tech")
    rc.set("test query", ["result2"], top_k=5, profile="tech")
    assert len(rc.get("test query", top_k=10, profile="tech")) == 1

    # 5. 统计
    svc = CacheService(manager=manager)
    stats = svc.get_statistics()
    assert stats["total_hits"] == 3  # 3 次 get 命中
    assert stats["total_misses"] == 0

    # 6. Dashboard
    dashboard = svc.get_dashboard_data()
    assert dashboard["summary"]["hit_rate"] == 1.0
    assert dashboard["summary"]["hits"] == 3

    # 7. 优化建议
    opt = CacheOptimizer(manager)
    suggestion = opt.suggest_ttl("query", 3600)
    assert suggestion["suggested_ttl"] >= 3600  # 100% 命中率建议延长 TTL
