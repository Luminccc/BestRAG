"""RankingEngine — 实验排名引擎。

根据综合评分对 Profile 排序，输出排名列表。
"""

from typing import Any, Dict, List, Tuple

from optimization.experiment.experiment import Experiment


class RankingEngine:
    """实验排名引擎。

    用法::

        engine = RankingEngine()
        rankings = engine.rank(experiments)
    """

    def __init__(self, weights: Dict[str, float] | None = None):
        self._weights = weights or {
            "recall": 0.4,
            "mrr": 0.3,
            "precision": 0.2,
            "latency": 0.1,
        }

    def rank(self, experiments: List[Experiment]) -> List[Tuple[Experiment, float]]:
        """按综合评分排序实验。

        Returns:
            [(experiment, score), ...] 按分数降序。
        """
        scored = [(exp, self._compute_score(exp)) for exp in experiments]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def _compute_score(self, experiment: Experiment) -> float:
        """计算实验综合评分。"""
        if experiment.result is None:
            return 0.0

        report = experiment.result
        recall = report.get_metric(f"recall@{experiment.k}")
        mrr = report.get_metric("mrr")
        precision = report.get_metric(f"precision@{experiment.k}")

        score = (
            recall * self._weights.get("recall", 0.4)
            + mrr * self._weights.get("mrr", 0.3)
            + precision * self._weights.get("precision", 0.2)
        )
        return round(score, 4)

    def get_best(self, experiments: List[Experiment]) -> Tuple[Experiment, float]:
        """获取最优实验。"""
        ranked = self.rank(experiments)
        return ranked[0] if ranked else (experiments[0] if experiments else None, 0.0)
