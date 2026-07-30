"""EvaluationService v3 — 评测服务增强版。

支持：
- 单次评测 / 批量 Benchmark
- Trace 分析集成
- 策略比较实验
- 检索调试
- Dashboard 数据输出
"""

from typing import Any, Callable, Dict, List, Optional

from core.logger import get_logger
from core.models.evaluation import EvaluationRun, EvaluationRunStatus, EvaluationResult
from core.models.trace import TraceType
from evaluation.analyzer import RetrievalTraceAnalyzer
from evaluation.benchmark.dataset import EvalSample, EvaluationDataset
from evaluation.benchmark.runner import BenchmarkRunner
from evaluation.core.result import EvaluationReport
from evaluation.debug import RetrievalDebugger
from evaluation.experiment import ExperimentManager, ExperimentReport
from evaluation.metric import (
    BaseMetric,
    HitRateMetric,
    MRRMetric,
    NDCGMetric,
    PrecisionMetric,
    RecallMetric,
)
from evaluation.retrieval.evaluator import RetrievalEvaluator
from trace.storage import BaseTraceStorage, MemoryTraceStorage

logger = get_logger("evaluation.service")


class EvaluationServiceV3:
    """评测服务 v3 — 统一评测入口。

    Usage::

        svc = EvaluationServiceV3()
        report = svc.run_benchmark(dataset, retrieve_fn)
        comparison = svc.compare_strategies(dataset, {"vector": ...})
    """

    def __init__(
        self,
        trace_storage: Optional[BaseTraceStorage] = None,
    ):
        self._retrieval_eval = RetrievalEvaluator()
        self._trace_analyzer = RetrievalTraceAnalyzer(storage=trace_storage)
        self._debugger = RetrievalDebugger()
        self._experiment = ExperimentManager()
        self._trace_storage = trace_storage or MemoryTraceStorage()
        self._runs: Dict[str, EvaluationRun] = {}

    # ── 单次评测 ──────────────────────────────────

    def evaluate_retrieval(
        self,
        results: list,
        expected_ids: set,
        k: int = 5,
    ) -> Dict[str, float]:
        """执行单次检索评测，返回指标字典。"""
        metrics = self._retrieval_eval.evaluate(results, expected_ids, k=k)
        return {m.name: m.value for m in metrics}

    # ── Benchmark ─────────────────────────────────

    def run_benchmark(
        self,
        dataset: EvaluationDataset,
        retrieve_fn: Callable,
        strategy_profile: Optional[Dict[str, str]] = None,
        scenario: str = "",
        k: int = 5,
    ) -> EvaluationReport:
        """运行批量 Benchmark。"""
        run = EvaluationRun(
            name=scenario or dataset.name,
            dataset_id=dataset.name,
            strategy=strategy_profile.get("strategy", "") if strategy_profile else "",
            profile=strategy_profile,
        )
        self._runs[run.id] = run
        run.status = EvaluationRunStatus.RUNNING

        runner = BenchmarkRunner(dataset)
        report = runner.run(retrieve_fn, strategy_profile, scenario, k=k)

        run.status = EvaluationRunStatus.COMPLETED
        return report

    # ── 实验比较 ──────────────────────────────────

    def compare_strategies(
        self,
        dataset: EvaluationDataset,
        strategies: Dict[str, Callable],
        experiment_name: str = "",
        k: int = 5,
    ) -> ExperimentReport:
        """比较多种策略。"""
        return self._experiment.compare_strategies(dataset, strategies, experiment_name, k=k)

    # ── Trace 分析 ────────────────────────────────

    def analyze_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """分析指定 Trace。"""
        trace = self._trace_storage.get(trace_id)
        if trace is None:
            return None
        return self._trace_analyzer.analyze(trace)

    def analyze_recent_retrievals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """分析最近的检索 Trace。"""
        traces = self._trace_storage.query(trace_type=TraceType.RETRIEVAL)[:limit]
        return self._trace_analyzer.analyze_multiple(traces)

    # ── 检索调试 ──────────────────────────────────

    def debug_retrieval(
        self,
        result_count: int,
        expected_count: int = 0,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """诊断检索问题。"""
        trace = None
        spans = None
        if trace_id:
            trace = self._trace_storage.get(trace_id)
            if trace:
                spans = self._trace_storage.get_spans(trace_id)
        return self._debugger.analyze(result_count, expected_count, trace, spans)

    # ── Dashboard API ─────────────────────────────

    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取 Dashboard 所需全部数据。"""
        traces = self._trace_storage.query(trace_type=TraceType.RETRIEVAL)

        # 聚合指标
        total_latency = 0.0
        total_results = 0
        for t in traces:
            metrics = self._trace_storage.get_metrics(t.id)
            for m in metrics:
                if m.metric_name == "latency_ms":
                    total_latency += m.value
                elif m.metric_name == "result_count":
                    total_results += int(m.value)

        return {
            "total_retrievals": len(traces),
            "avg_latency_ms": round(total_latency / len(traces), 2) if traces else 0,
            "total_results": total_results,
            "trace_analysis": self.analyze_recent_retrievals(5),
        }

    def get_runs(self) -> List[Dict[str, Any]]:
        """获取所有评测任务。"""
        return [r.to_dict() for r in self._runs.values()]
