"""BestRAG v0.3 Phase 3 测试 — Evaluation Intelligence Framework。

覆盖：
1. Model 测试     — EvaluationRun / EvaluationResult / EvaluationCase
2. Metric 测试    — Recall / Precision / MRR / NDCG / HitRate / Diversity / Coverage
3. Analyzer 测试  — RetrievalTraceAnalyzer
4. Debug 测试     — RetrievalDebugger
5. Dataset 测试   — DatasetManager 创建/版本/导入导出
6. Experiment 测试 — ExperimentManager 策略比较
7. Service 测试   — EvaluationServiceV3
8. Config 测试    — EvaluationConfigV3
9. 集成测试       — Dataset → Retrieval → Trace → Evaluation → Report

运行::

    uv run pytest tests/core/v03/evaluation/test_phase3.py -v
"""

import pytest
import json
import tempfile
import os
from datetime import datetime

from core.models.evaluation import (
    EvaluationRun, EvaluationRunStatus,
    EvaluationResult, EvaluationCase,
)
from core.models.trace import Trace, TraceType, TraceStatus, Span, Metric
from evaluation.metric import (
    RecallMetric, PrecisionMetric, MRRMetric, NDCGMetric,
    HitRateMetric, DiversityScore, CoverageScore,
)
from evaluation.analyzer import RetrievalTraceAnalyzer
from evaluation.debug import RetrievalDebugger
from evaluation.dataset import DatasetManager
from evaluation.experiment import ExperimentManager, ExperimentReport
from evaluation.service import EvaluationServiceV3
from evaluation.benchmark.dataset import EvalSample, EvaluationDataset
from evaluation.registry import register_evaluation_module
from core.config_models.evaluation_v3 import EvaluationConfigV3
from core.config import CoreConfig
from core.registry.center import reset_registry
from trace.storage import MemoryTraceStorage


# ═══════════════════════════════════════════════════
# Fisher
# ═══════════════════════════════════════════════════

@pytest.fixture
def storage():
    return MemoryTraceStorage()


@pytest.fixture(autouse=True)
def _reset():
    reset_registry()


# ═══════════════════════════════════════════════════
# Test 1: Model 测试
# ═══════════════════════════════════════════════════

class TestEvaluationModels:
    def test_evaluation_run_default(self):
        run = EvaluationRun(name="test_run")
        assert run.name == "test_run"
        assert run.status == EvaluationRunStatus.PENDING
        assert run.id is not None

    def test_evaluation_run_completed(self):
        run = EvaluationRun(name="test", status=EvaluationRunStatus.COMPLETED)
        run.completed_at = datetime.now()
        d = run.to_dict()
        assert d["status"] == "completed"
        assert d["completed_at"] is not None

    def test_evaluation_result(self):
        result = EvaluationResult(
            run_id="run_1",
            metrics={"recall@5": 0.92, "mrr": 0.85},
            trace_ids=["trace_1"],
        )
        assert result.run_id == "run_1"
        assert result.metrics["recall@5"] == 0.92
        assert len(result.trace_ids) == 1

    def test_evaluation_case(self):
        case = EvaluationCase(
            query="什么是 RAG?",
            expected_documents=["doc_1", "doc_2"],
            retrieved_documents=["doc_1", "doc_3"],
            feedback="good",
        )
        assert case.query == "什么是 RAG?"
        assert len(case.expected_documents) == 2


# ═══════════════════════════════════════════════════
# Test 2: Metric 测试
# ═══════════════════════════════════════════════════

class TestRetrievalMetrics:
    def test_recall(self):
        metric = RecallMetric()
        val = metric.calculate(retrieved=["a", "b", "c"], expected={"a", "d"}, k=5)
        assert val == 0.5  # 1/2

    def test_recall_empty_expected(self):
        metric = RecallMetric()
        val = metric.calculate(retrieved=["a"], expected=set(), k=5)
        assert val == 0.0

    def test_precision(self):
        metric = PrecisionMetric()
        val = metric.calculate(retrieved=["a", "b", "c"], expected={"a", "d", "e"}, k=5)
        assert val == 1.0 / 3  # 1/3

    def test_mrr(self):
        metric = MRRMetric()
        val = metric.calculate(retrieved=["x", "a", "b"], expected={"a"})
        assert val == 0.5  # 1/2

    def test_mrr_not_found(self):
        metric = MRRMetric()
        val = metric.calculate(retrieved=["x", "y"], expected={"a"})
        assert val == 0.0

    def test_ndcg(self):
        metric = NDCGMetric()
        val = metric.calculate(retrieved=["a", "b", "c"], expected={"a"}, k=5)
        assert val > 0

    def test_hit_rate_hit(self):
        metric = HitRateMetric()
        val = metric.calculate(retrieved=["a", "b"], expected={"a"})
        assert val == 1.0

    def test_hit_rate_miss(self):
        metric = HitRateMetric()
        val = metric.calculate(retrieved=["x", "y"], expected={"a"})
        assert val == 0.0

    def test_diversity_default(self):
        metric = DiversityScore()
        val = metric.calculate(retrieved=["a", "b", "c"])
        assert val == 1.0  # 无 source_fn 时默认最大

    def test_coverage_default(self):
        metric = CoverageScore()
        val = metric.calculate(retrieved=["a", "b"])
        assert val == 1.0

    def test_metric_name(self):
        assert RecallMetric().name() == "recall"
        assert PrecisionMetric().name() == "precision"
        assert MRRMetric().name() == "mrr"
        assert NDCGMetric().name() == "ndcg"
        assert HitRateMetric().name() == "hit_rate"
        assert DiversityScore().name() == "diversity"
        assert CoverageScore().name() == "coverage"


# ═══════════════════════════════════════════════════
# Test 3: Analyzer 测试
# ═══════════════════════════════════════════════════

class TestRetrievalTraceAnalyzer:
    def test_analyze_empty(self, storage):
        analyzer = RetrievalTraceAnalyzer(storage=storage)
        t = Trace(trace_type=TraceType.RETRIEVAL, status=TraceStatus.SUCCESS)
        result = analyzer.analyze(t)
        assert result["trace_id"] == t.id
        assert result["latency"] == {}
        assert result["retriever_contribution"] == {}

    def test_analyze_with_spans(self, storage):
        t = Trace(trace_type=TraceType.RETRIEVAL)
        storage.save(t)
        s1 = Span(trace_id=t.id, name="retriever_vector")
        s1.attributes["result_count"] = 5
        storage.save_span(s1)
        s2 = Span(trace_id=t.id, name="fusion")
        s2.attributes["method"] = "rrf"
        s2.attributes["input_count"] = 2
        storage.save_span(s2)

        analyzer = RetrievalTraceAnalyzer(storage=storage)
        result = analyzer.analyze(t)
        assert result["retriever_contribution"]["vector"] == 5
        assert result["fusion_effect"]["method"] == "rrf"

    def test_analyze_failure(self, storage):
        t = Trace(trace_type=TraceType.RETRIEVAL, status=TraceStatus.FAILED)
        storage.save(t)
        s = Span(trace_id=t.id, name="retriever")
        s.attributes["error"] = "connection timeout"
        s.status = "error"
        storage.save_span(s)

        analyzer = RetrievalTraceAnalyzer(storage=storage)
        result = analyzer.analyze(t)
        assert "connection timeout" in result["failure_reason"]


# ═══════════════════════════════════════════════════
# Test 4: Debug 测试
# ═══════════════════════════════════════════════════

class TestRetrievalDebugger:
    def test_no_results(self):
        debugger = RetrievalDebugger()
        result = debugger.analyze(result_count=0)
        assert "no_results" in result["issues"]

    def test_query_empty(self):
        debugger = RetrievalDebugger()
        result = debugger.analyze_query(query="")
        assert "empty_query" in result["issues"]

    def test_query_short(self):
        debugger = RetrievalDebugger()
        result = debugger.analyze_query(query="ab")
        assert "query_too_short" in result["issues"]

    def test_query_normal(self):
        debugger = RetrievalDebugger()
        result = debugger.analyze_query(query="deploy RAG", rewritten_query="deploy RAG")
        assert len(result["issues"]) == 0

    def test_chunk_empty(self):
        debugger = RetrievalDebugger()
        result = debugger.analyze_chunk(chunk_count=0)
        assert "no_chunks" in result["issues"]

    def test_chunk_single(self):
        debugger = RetrievalDebugger()
        result = debugger.analyze_chunk(chunk_count=1)
        assert "single_chunk" in result["issues"]

    def test_analyze_with_trace(self, storage):
        t = Trace(trace_type=TraceType.RETRIEVAL)
        storage.save(t)
        s = Span(trace_id=t.id, name="retriever_vector")
        s.attributes["error"] = "timeout"
        storage.save_span(s)

        debugger = RetrievalDebugger()
        result = debugger.analyze(
            result_count=0,
            trace=t,
            spans=[s],
        )
        assert "no_results" in result["issues"]
        assert "retriever_vector_error" in result["issues"]


# ═══════════════════════════════════════════════════
# Test 5: Dataset 测试
# ═══════════════════════════════════════════════════

class TestDatasetManager:
    def test_create_dataset(self):
        mgr = DatasetManager()
        ds = mgr.create_dataset("test_ds", [
            EvalSample(query="q1", expected_ids={"d1"}),
        ])
        assert ds.name == "test_ds"
        assert ds.size == 1

    def test_get_dataset(self):
        mgr = DatasetManager()
        mgr.create_dataset("test")
        assert mgr.get_dataset("test") is not None
        assert mgr.get_dataset("nonexistent") is None

    def test_list_datasets(self):
        mgr = DatasetManager()
        mgr.create_dataset("a")
        mgr.create_dataset("b")
        assert set(mgr.list_datasets()) == {"a", "b"}

    def test_create_version(self):
        mgr = DatasetManager()
        v2 = mgr.create_version("tech_qa", "v2")
        assert v2.name == "tech_qa_v2"

    def test_export_import(self):
        mgr = DatasetManager()
        ds = mgr.create_dataset("export_test", [
            EvalSample(query="q1", expected_ids={"d1", "d2"}),
        ])
        data = DatasetManager.export_to_dict(ds)
        assert data["name"] == "export_test"
        assert data["size"] == 1
        assert "d1" in data["samples"][0]["expected_ids"]

    def test_export_import_json(self):
        mgr = DatasetManager()
        ds = mgr.create_dataset("json_test", [
            EvalSample(query="test query", expected_ids={"doc_1"}),
        ])
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
            DatasetManager.save_dataset(ds, path)

        loaded = DatasetManager.load_dataset(path)
        assert loaded.name == "json_test"
        assert loaded.size == 1
        os.unlink(path)


# ═══════════════════════════════════════════════════
# Test 6: Experiment 测试
# ═══════════════════════════════════════════════════

class TestExperimentManager:
    def test_experiment_report(self):
        from evaluation.core.result import EvaluationReport
        from evaluation.core.metric import MetricResult

        report = ExperimentReport(name="test_exp")
        r1 = EvaluationReport(
            scenario="test",
            metrics=[MetricResult(name="recall@5", value=0.9)],
        )
        r2 = EvaluationReport(
            scenario="test",
            metrics=[MetricResult(name="recall@5", value=0.8)],
        )
        report.add_result("strategy_a", r1)
        report.add_result("strategy_b", r2)

        assert report.compare("recall@5") == {"strategy_a": 0.9, "strategy_b": 0.8}
        assert report.get_winner() == "strategy_a"
        assert "strategy_a" in report.to_dict()["strategies"]


# ═══════════════════════════════════════════════════
# Test 7: Service 测试
# ═══════════════════════════════════════════════════

class TestEvaluationServiceV3:
    def test_evaluate_retrieval(self):
        from retrieval.retriever.model import RetrievalResult
        svc = EvaluationServiceV3()
        results = [
            RetrievalResult(chunk_id="d1", content="a", score=0.9, metadata={}),
            RetrievalResult(chunk_id="d3", content="c", score=0.7, metadata={}),
        ]
        metrics = svc.evaluate_retrieval(results, {"d1", "d2"}, k=5)
        assert "recall@5" in metrics
        assert metrics["recall@5"] == 0.5  # 1/2

    def test_debug_retrieval(self):
        svc = EvaluationServiceV3()
        result = svc.debug_retrieval(result_count=0)
        assert "no_results" in result["issues"]

    def test_get_dashboard_data_empty(self):
        svc = EvaluationServiceV3()
        data = svc.get_dashboard_data()
        assert data["total_retrievals"] == 0
        assert data["avg_latency_ms"] == 0

    def test_get_runs_empty(self):
        svc = EvaluationServiceV3()
        assert svc.get_runs() == []


# ═══════════════════════════════════════════════════
# Test 8: Config 测试
# ═══════════════════════════════════════════════════

def test_evaluation_config_v3_defaults():
    cfg = EvaluationConfigV3()
    assert cfg.enabled is True
    assert "recall" in cfg.metrics
    assert "ndcg" in cfg.metrics
    assert cfg.trace_analysis is True


def test_core_config_has_evaluation_v3():
    cfg = CoreConfig()
    assert hasattr(cfg, "evaluation_v3")
    assert cfg.evaluation_v3.enabled is True


# ═══════════════════════════════════════════════════
# Test 9: Registry 测试
# ═══════════════════════════════════════════════════

def test_register_evaluation_module():
    register_evaluation_module()
    from core.registry import get_registry
    rc = get_registry()
    assert rc.model.has("RecallMetric")
    assert rc.model.has("MRRMetric")
    assert rc.model.has("HitRateMetric")
    assert rc.model.has("DiversityScore")
    assert rc.service.has("trace_analyzer")
    assert rc.service.has("retrieval_debugger")


# ═══════════════════════════════════════════════════
# Test 10: 端到端集成测试
# ═══════════════════════════════════════════════════

def test_end_to_end_evaluation():
    """完整流程：Dataset -> Retrieval -> Trace -> Evaluation -> Report。"""
    from retrieval.retriever.model import RetrievalResult

    # 1. 创建数据集
    ds = EvaluationDataset(name="e2e_test")
    ds.add_sample(EvalSample(query="test", expected_ids={"d1"}))
    ds.add_sample(EvalSample(query="hello", expected_ids={"d2"}))

    # 2. 模拟检索函数
    def mock_retrieve(query, top_k=5, **kw):
        return [RetrievalResult(chunk_id="d1", content="result", score=0.9, metadata={})]

    # 3. 评测
    svc = EvaluationServiceV3()
    report = svc.run_benchmark(ds, mock_retrieve, scenario="e2e", k=5)

    assert report.scenario == "e2e"
    assert report.metadata.get("dataset_size", 0) >= 2
    assert report.metrics is not None

    # 4. 指标验证
    recall = report.get_metric("recall@5")
    assert recall >= 0  # 至少有一个样本命中


def test_end_to_end_trace_analysis():
    """完整流程：Trace -> Analyzer -> Service。"""
    from trace import DefaultTraceCollector

    storage = MemoryTraceStorage()
    collector = DefaultTraceCollector(storage=storage)
    from trace import TraceContext
    ctx = TraceContext(collector=collector)

    # 创建检索 Trace
    ctx.start_trace(TraceType.RETRIEVAL, metadata={"query": "test"})
    with ctx.span("retriever_vector", result_count=3):
        pass
    with ctx.span("retriever_bm25", result_count=2):
        pass
    with ctx.span("fusion", method="rrf", input_count=2, output_count=5):
        pass
    ctx.record_metric("latency_ms", 150.0)
    ctx.end_trace(TraceStatus.SUCCESS)

    # 通过 Service 分析
    svc = EvaluationServiceV3(trace_storage=storage)
    analysis = svc.analyze_recent_retrievals(limit=5)
    assert len(analysis) >= 1
    assert analysis[0]["retriever_contribution"]["vector"] == 3
