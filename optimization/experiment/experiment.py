"""Experiment — 优化实验定义。

一次实验包含：数据集 + Profile + Pipeline + Evaluation。
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from evaluation.benchmark.dataset import EvaluationDataset
from evaluation.core.result import EvaluationReport
from optimization.profile.model import RAGProfile


@dataclass
class Experiment:
    """优化实验。

    Attributes:
        name:            实验名称。
        dataset:         评测数据集。
        profile:         使用的 RAG Profile。
        retrieve_fn:     检索函数（由上层提供）。
        k:               Recall@K 的 K 值。
        result:          实验结果（运行后填充）。
        metadata:        额外信息。
    """
    name: str = ""
    dataset: Optional[EvaluationDataset] = None
    profile: Optional[RAGProfile] = None
    retrieve_fn: Optional[Callable] = None
    k: int = 5
    result: Optional[EvaluationReport] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def score(self) -> float:
        """获取综合评分。"""
        if self.result is None:
            return 0.0
        recall = self.result.get_metric(f"recall@{self.k}")
        mrr = self.result.get_metric("mrr")
        precision = self.result.get_metric(f"precision@{self.k}")
        # 加权综合评分
        return recall * 0.4 + mrr * 0.3 + precision * 0.2
