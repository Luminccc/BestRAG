"""BenchmarkRunner — 评测批量运行器。

对策略组合执行批量测试，生成评测报告。
"""

from typing import Any, Callable, Dict, List, Optional

from evaluation.benchmark.dataset import EvaluationDataset
from evaluation.core.result import EvaluationReport
from evaluation.retrieval.evaluator import RetrievalEvaluator


class BenchmarkRunner:
    """评测运行器。

    用法::

        runner = BenchmarkRunner(dataset)
        report = runner.run(retrieve_fn)
    """

    def __init__(self, dataset: EvaluationDataset):
        self._dataset = dataset
        self._evaluator = RetrievalEvaluator()

    def run(
        self,
        retrieve_fn: Callable,
        strategy_profile: Optional[Dict[str, str]] = None,
        scenario: str = "",
        k: int = 5,
        **kwargs: Any,
    ) -> EvaluationReport:
        """运行批量评测。

        Args:
            retrieve_fn: 检索函数，接受 query 返回结果列表。
            strategy_profile: 策略配置描述。
            scenario: 场景名称。
            k: Recall/Precision@K 的 K 值。

        Returns:
            聚合后的评测报告。
        """
        profile = dict(strategy_profile) if strategy_profile else {}

        all_metrics: Dict[str, List[float]] = {}

        for sample in self._dataset.samples:
            try:
                results = retrieve_fn(sample.query, top_k=k, **kwargs)
            except Exception:
                results = []

            metrics = self._evaluator.evaluate(
                results, expected_ids=sample.expected_ids, k=k
            )

            for m in metrics:
                if m.name not in all_metrics:
                    all_metrics[m.name] = []
                all_metrics[m.name].append(m.value)

        # 计算平均指标
        from evaluation.core.metric import MetricResult
        avg_metrics = [
            MetricResult(
                name=name,
                value=sum(values) / len(values),
                metadata={"count": len(values)},
            )
            for name, values in all_metrics.items()
        ]

        report = EvaluationReport(
            scenario=scenario or self._dataset.name,
            strategy_profile=profile,
            metrics=avg_metrics,
            metadata={
                "dataset_size": self._dataset.size,
                "k": k,
            },
        )
        return report
