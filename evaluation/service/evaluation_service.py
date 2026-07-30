"""EvaluationService — 评测服务入口。

对外提供 evaluate() 和 benchmark() 接口。
"""

from typing import Any, Callable, Dict, List, Optional

from evaluation.benchmark.dataset import EvaluationDataset
from evaluation.benchmark.runner import BenchmarkRunner
from evaluation.core.result import EvaluationReport
from evaluation.retrieval.evaluator import RetrievalEvaluator


class EvaluationService:
    """评测服务 — 统一评测入口。

    Usage::

        svc = EvaluationService()
        report = svc.benchmark(dataset, retrieve_fn)
    """

    def __init__(self):
        self._retrieval_eval = RetrievalEvaluator()

    def evaluate_retrieval(
        self,
        results: list,
        expected_ids: set,
        k: int = 5,
    ) -> List:
        """执行单次检索评测。"""
        return self._retrieval_eval.evaluate(results, expected_ids, k)

    def benchmark(
        self,
        dataset: EvaluationDataset,
        retrieve_fn: Callable,
        strategy_profile: Optional[Dict[str, str]] = None,
        scenario: str = "",
        k: int = 5,
    ) -> EvaluationReport:
        """执行批量 Benchmark。"""
        runner = BenchmarkRunner(dataset)
        return runner.run(retrieve_fn, strategy_profile, scenario, k=k)

    def compare_strategies(
        self,
        dataset: EvaluationDataset,
        strategies: Dict[str, Callable],
        k: int = 5,
    ) -> Dict[str, EvaluationReport]:
        """比较多种策略的评测结果。

        Args:
            dataset: 评测数据集。
            strategies: 策略名 → 检索函数 映射。
            k: Recall/Precision@K 的 K 值。

        Returns:
            策略名 → 评测报告 映射。
        """
        reports = {}
        for name, fn in strategies.items():
            reports[name] = self.benchmark(
                dataset, fn, strategy_profile={"retrieval": name}, k=k
            )
        return reports
