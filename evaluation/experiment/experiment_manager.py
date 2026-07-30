"""ExperimentManager — 评测实验管理。

支持策略对比实验（A/B Test），生成实验报告。
连接 Phase 5 Optimization Framework。
"""

from typing import Any, Callable, Dict, List, Optional

from core.logger import get_logger
from evaluation.benchmark.dataset import EvaluationDataset
from evaluation.benchmark.runner import BenchmarkRunner
from evaluation.core.result import EvaluationReport

logger = get_logger("evaluation.experiment")


class ExperimentReport:
    """实验报告 — 对比多种策略的评测结果。"""

    def __init__(self, name: str = ""):
        self.name = name
        self.strategies: Dict[str, EvaluationReport] = {}

    def add_result(self, strategy_name: str, report: EvaluationReport) -> None:
        self.strategies[strategy_name] = report

    def get_winner(self, metric_name: str = "recall@5") -> Optional[str]:
        """获取指定指标上的最优策略名称。"""
        best_name = None
        best_value = float("-inf")
        for name, report in self.strategies.items():
            val = report.get_metric(metric_name)
            if val > best_value:
                best_value = val
                best_name = name
        return best_name

    def compare(self, metric_name: str) -> Dict[str, float]:
        """比较所有策略在指定指标上的值。"""
        return {
            name: report.get_metric(metric_name)
            for name, report in self.strategies.items()
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "strategies": {
                name: report.to_dict() for name, report in self.strategies.items()
            },
            "winner": self.get_winner(),
        }


class ExperimentManager:
    """实验管理器。

    支持：
    - 比较不同 Embedding 模型
    - 比较不同 Chunk 策略
    - 比较不同检索器
    """

    def __init__(self):
        self._experiments: Dict[str, ExperimentReport] = {}

    def compare_strategies(
        self,
        dataset: EvaluationDataset,
        strategies: Dict[str, Callable],
        experiment_name: str = "",
        k: int = 5,
    ) -> ExperimentReport:
        """比较多种策略。

        Args:
            dataset: 评测数据集。
            strategies: 策略名 → 检索函数 映射。
            experiment_name: 实验名称。
            k: 评测 K 值。

        Returns:
            实验报告。
        """
        report = ExperimentReport(name=experiment_name or "experiment")
        for name, fn in strategies.items():
            runner = BenchmarkRunner(dataset)
            eval_report = runner.run(
                fn,
                strategy_profile={"strategy": name},
                scenario=dataset.name,
                k=k,
            )
            report.add_result(name, eval_report)
            logger.info(f"策略评测完成: {name}")

        self._experiments[report.name] = report
        return report

    def get_report(self, name: str) -> Optional[ExperimentReport]:
        """获取已保存的实验报告。"""
        return self._experiments.get(name)
