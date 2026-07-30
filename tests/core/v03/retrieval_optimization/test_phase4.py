"""BestRAG v0.3 Phase 4 测试 — Retrieval Optimization & Knowledge Intelligence。

覆盖：
1. Model 测试      — RetrievalProfile / RetrievalAnalysis / OptimizationSuggestion
2. Query 测试      — QueryAnalyzer 类型识别
3. Selector 测试   — AdaptiveRetrieverSelector 策略选择
4. Knowledge 测试  — KnowledgeAnalyzer 质量分析
5. Feedback 测试   — FeedbackAnalyzer 闭环
6. Optimizer 测试  — RetrievalOptimizer
7. Service 测试    — RetrievalOptimizationService
8. Config 测试     — RetrievalOptimizationConfig

运行::

    uv run pytest tests/core/v03/retrieval_optimization/test_phase4.py -v
"""

import pytest

from core.models.retrieval import RetrievalProfile, RetrievalAnalysis, OptimizationSuggestion
from retrieval.intelligence import QueryAnalyzer, AdaptiveRetrieverSelector
from retrieval.intelligence.query import QueryIntent
from knowledge.intelligence import KnowledgeAnalyzer
from optimization.feedback import FeedbackAnalyzer
from optimization.optimizer.optimizer import RetrievalOptimizer
from optimization.service.retrieval_optimization_service import RetrievalOptimizationService
from core.config_models.retrieval_optimization import RetrievalOptimizationConfig
from core.config import CoreConfig
from core.models.trace import Trace, TraceType, TraceStatus, Metric
from trace.storage import MemoryTraceStorage


@pytest.fixture
def storage():
    """MemoryTraceStorage fixture for tests needing trace storage."""
    return MemoryTraceStorage()


# ═══════════════════════════════════════════════════
# Test 1: Model 测试
# ═══════════════════════════════════════════════════

class TestRetrievalModels:
    def test_retrieval_profile_default(self):
        p = RetrievalProfile(name="test")
        assert p.name == "test"
        assert p.retrievers == ["vector"]
        assert p.fusion == "rrf"
        assert p.top_k == 10

    def test_retrieval_profile_custom(self):
        p = RetrievalProfile(
            name="tech",
            retrievers=["vector", "bm25"],
            fusion="weighted",
            reranker="bge",
            top_k=15,
        )
        assert "bm25" in p.retrievers
        assert p.reranker == "bge"
        assert p.top_k == 15
        d = p.to_dict()
        assert d["retrievers"] == ["vector", "bm25"]

    def test_retrieval_analysis(self):
        a = RetrievalAnalysis(
            query="test", retrieval_quality=0.8,
            recommendations=["尝试更换 Embedding"],
        )
        assert a.query == "test"
        assert a.retrieval_quality == 0.8
        assert len(a.recommendations) == 1

    def test_optimization_suggestion(self):
        s = OptimizationSuggestion(
            suggestion_type="embedding_change",
            target="embedding",
            value_from="bge-m3",
            value_to="text-embedding-3",
            reason="低语义相似度",
            score_impact=-0.3,
        )
        assert s.suggestion_type == "embedding_change"
        assert s.value_to == "text-embedding-3"


# ═══════════════════════════════════════════════════
# Test 2: Query 分析测试
# ═══════════════════════════════════════════════════

class TestQueryAnalyzer:
    def test_simple_query(self):
        intent = QueryAnalyzer.analyze("什么是 RAG?")
        assert intent.type == "simple"
        assert intent.retrieval_mode == "vector"

    def test_technical_query(self):
        intent = QueryAnalyzer.analyze("How to configure Milvus cluster?")
        assert intent.type == "technical"
        assert intent.retrieval_mode == "hybrid"
        assert intent.need_metadata is True

    def test_exact_query(self):
        intent = QueryAnalyzer.analyze('"version 2.1.0"')
        assert intent.type == "exact"
        assert intent.retrieval_mode == "bm25"
        assert intent.retrieval_mode == "bm25"

    def test_multi_hop_query(self):
        intent = QueryAnalyzer.analyze("Compare Milvus and Weaviate deployment differences")
        assert intent.type == "multi_hop"
        assert intent.retrieval_mode == "hybrid"

    def test_empty_query(self):
        intent = QueryAnalyzer.analyze("")
        assert intent.type == "simple"

    def test_keywords_extraction(self):
        intent = QueryAnalyzer.analyze("How to deploy Milvus cluster?")
        assert len(intent.keywords) >= 2

    def test_query_intent_to_dict(self):
        intent = QueryIntent(query_type="technical", retrieval_mode="hybrid")
        d = intent.to_dict()
        assert d["type"] == "technical"
        assert d["retrieval_mode"] == "hybrid"


# ═══════════════════════════════════════════════════
# Test 3: Selector 测试
# ═══════════════════════════════════════════════════

class TestAdaptiveRetrieverSelector:
    def test_select_for_technical(self):
        selector = AdaptiveRetrieverSelector()
        profile = selector.select("How to configure Milvus cluster?")
        assert "bm25" in profile.retrievers
        assert profile.reranker == "bge"

    def test_select_for_simple(self):
        selector = AdaptiveRetrieverSelector()
        profile = selector.select("什么是 RAG?")
        assert profile.retrievers == ["vector"]

    def test_select_for_exact(self):
        selector = AdaptiveRetrieverSelector()
        profile = selector.select('"version 2.0"')
        assert profile.retrievers == ["bm25"]
        assert profile.top_k == 5

    def test_select_from_intent(self):
        selector = AdaptiveRetrieverSelector()
        intent = QueryIntent(query_type="technical", retrieval_mode="hybrid")
        profile = selector.select_from_intent(intent)
        assert profile.name == "adaptive_technical"

    def test_to_rag_profile(self):
        selector = AdaptiveRetrieverSelector()
        rp = RetrievalProfile(name="test", retrievers=["vector", "bm25"])
        rag = selector.to_rag_profile(rp)
        assert rag.name == "test"
        assert "vector" in rag.retrieval_strategies

    def test_faq_kb_type(self):
        selector = AdaptiveRetrieverSelector()
        profile = selector.select("如何退款?", kb_type="faq")
        assert profile.retrievers == ["bm25"]
        assert profile.top_k == 5


# ═══════════════════════════════════════════════════
# Test 4: Knowledge Analyzer 测试
# ═══════════════════════════════════════════════════

class TestKnowledgeAnalyzer:
    def test_analyze_documents_healthy(self):
        storage = MemoryTraceStorage()
        analyzer = KnowledgeAnalyzer(trace_storage=storage)
        results = analyzer.analyze_documents([], [])
        assert results == []

    def test_analyze_trace_quality_not_found(self):
        analyzer = KnowledgeAnalyzer()
        result = analyzer.analyze_trace_quality("nonexistent")
        assert "error" in result

    def test_analyze_trace_quality_healthy(self, storage):
        t = Trace(trace_type=TraceType.RETRIEVAL)
        storage.save(t)
        storage.save_metric(Metric(trace_id=t.id, metric_name="result_count", value=5))
        storage.save_metric(Metric(trace_id=t.id, metric_name="latency_ms", value=100))

        analyzer = KnowledgeAnalyzer(trace_storage=storage)
        result = analyzer.analyze_trace_quality(t.id)
        assert result["healthy"] is True
        assert result["result_count"] == 5

    def test_detect_missing_knowledge(self):
        analyzer = KnowledgeAnalyzer()
        findings = analyzer.detect_missing_knowledge(
            ["什么是 RAG 系统?", "short"],
            {"什么是 RAG 系统?": 0, "short": 0},
        )
        types = [f["type"] for f in findings]
        assert "knowledge_missing" in types
        assert "retrieval_failure" in types


# ═══════════════════════════════════════════════════
# Test 5: Feedback 测试
# ═══════════════════════════════════════════════════

class TestFeedbackAnalyzer:
    def test_collect_failures_empty(self):
        storage = MemoryTraceStorage()
        fb = FeedbackAnalyzer(trace_storage=storage)
        failures = fb.collect_failures()
        assert failures == []

    def test_collect_failures_with_data(self, storage):
        t = Trace(trace_type=TraceType.RETRIEVAL, metadata={"query": "test"})
        storage.save(t)
        storage.save_metric(Metric(trace_id=t.id, metric_name="result_count", value=0))

        fb = FeedbackAnalyzer(trace_storage=storage)
        failures = fb.collect_failures()
        assert len(failures) == 1
        assert failures[0]["result_count"] == 0

    def test_generate_suggestions(self):
        fb = FeedbackAnalyzer()
        suggestions = fb.generate_suggestions()
        assert suggestions == []


# ═══════════════════════════════════════════════════
# Test 6: Optimizer 测试
# ═══════════════════════════════════════════════════

class TestRetrievalOptimizer:
    def test_optimize_component(self):
        optimizer = RetrievalOptimizer()
        suggestions = optimizer.optimize_component(
            "chunk_strategy",
            "recursive",
            ["recursive", "semantic", "hierarchical"],
        )
        assert len(suggestions) == 2
        assert suggestions[0].suggestion_type == "chunk_strategy_change"
        assert suggestions[0].value_to == "semantic"

    def test_optimize_component_no_alternatives(self):
        optimizer = RetrievalOptimizer()
        suggestions = optimizer.optimize_component("fusion", "rrf", ["rrf"])
        assert len(suggestions) == 0


# ═══════════════════════════════════════════════════
# Test 7: Service 测试
# ═══════════════════════════════════════════════════

class TestRetrievalOptimizationService:
    def test_analyze_query(self):
        svc = RetrievalOptimizationService()
        result = svc.analyze_query("How to configure Milvus cluster?")
        assert result["query"] == "How to configure Milvus cluster?"
        assert "intent" in result
        assert result["intent"]["type"] == "technical"

    def test_recommend_strategy(self):
        svc = RetrievalOptimizationService()
        result = svc.recommend_strategy("What is RAG?")
        assert result["intent"] == "simple"
        assert "retrievers" in result

    def test_get_quality_report(self):
        svc = RetrievalOptimizationService()
        report = svc.get_quality_report()
        assert "total_failures" in report
        assert "suggestions" in report

    def test_optimize_profile_not_found(self):
        svc = RetrievalOptimizationService()
        result = svc.optimize_profile("nonexistent")
        assert "error" in result

    def test_optimize_profile_default(self):
        svc = RetrievalOptimizationService()
        result = svc.optimize_profile("default")
        assert "profile" in result
        assert "optimization_suggestions" in result


# ═══════════════════════════════════════════════════
# Test 8: Config 测试
# ═══════════════════════════════════════════════════

def test_retrieval_optimization_config_defaults():
    cfg = RetrievalOptimizationConfig()
    assert cfg.enabled is True
    assert cfg.adaptive_selector is True
    assert cfg.knowledge_analysis is True


def test_core_config_has_retrieval_optimization():
    cfg = CoreConfig()
    assert hasattr(cfg, "retrieval_optimization")
    assert cfg.retrieval_optimization.enabled is True


# ═══════════════════════════════════════════════════
# Test 9: 端到端集成
# ═══════════════════════════════════════════════════

def test_end_to_end_query_to_recommendation():
    """Query -> Analysis -> Strategy -> Recommendations 完整流程。"""
    svc = RetrievalOptimizationService()

    # 1. 分析 Query
    query = "How to deploy Milvus cluster?"
    analysis = svc.analyze_query(query)
    assert analysis["intent"]["type"] == "technical"
    assert analysis["intent"]["retrieval_mode"] == "hybrid"

    # 2. 推荐策略
    strategy = svc.recommend_strategy(query)
    assert "vector" in strategy["retrievers"]
    assert "bm25" in strategy["retrievers"]

    # 3. 获取质量报告
    report = svc.get_quality_report()
    assert report is not None

    # 4. 获取优化建议
    optimization = svc.optimize_profile("default")
    assert len(optimization["optimization_suggestions"]) > 0
