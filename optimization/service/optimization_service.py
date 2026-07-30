"""OptimizationService — 优化服务入口。

对外提供 optimize() 和 recommend() 接口。
"""

from typing import Callable, Dict, List, Optional, Tuple

from evaluation.benchmark.dataset import EvaluationDataset
from optimization.experiment.experiment import Experiment
from optimization.experiment.runner import ExperimentRunner
from optimization.optimizer.ranking import RankingEngine
from optimization.optimizer.selector import ProfileSelector
from optimization.profile.model import RAGProfile
from optimization.profile.registry import ProfileRegistry


class OptimizationService:
    """优化服务 — 统一优化入口。

    Usage::

        svc = OptimizationService()
        # 自动优化
        best, report = svc.optimize(dataset, retrieve_fn)
        # 推荐 Profile
        profile = svc.recommend({"type": "technical"})
    """

    def __init__(self):
        self._registry = ProfileRegistry()
        self._selector = ProfileSelector(self._registry)
        self._ranking = RankingEngine()

    @property
    def registry(self) -> ProfileRegistry:
        return self._registry

    def optimize(
        self,
        dataset: EvaluationDataset,
        retrieve_fn: Callable,
        profiles: Optional[List[RAGProfile]] = None,
        k: int = 5,
    ) -> Tuple[Optional[RAGProfile], float]:
        """对知识库执行全自动优化。

        Args:
            dataset: 评测数据集。
            retrieve_fn: 检索函数。
            profiles: 待评测的 Profile 列表（默认使用全部注册的 Profile）。
            k: Recall@K。

        Returns:
            (best_profile, best_score)
        """
        profiles = profiles or self._registry.list()
        runner = ExperimentRunner(dataset, retrieve_fn, k=k)
        experiments = runner.run_all(profiles)
        return self._ranking.get_best(experiments)

    def recommend(self, kb_metadata: Dict) -> RAGProfile:
        """根据知识库特征推荐 Profile。"""
        return self._selector.select_for_knowledge_base(kb_metadata)

    def compare_profiles(
        self,
        dataset: EvaluationDataset,
        retrieve_fn: Callable,
        k: int = 5,
    ) -> List[Experiment]:
        """比较所有注册 Profile 的效果。"""
        runner = ExperimentRunner(dataset, retrieve_fn, k=k)
        return runner.run_all(self._registry.list())

    def register_profile(self, profile: RAGProfile) -> None:
        """注册自定义 Profile。"""
        self._registry.register(profile)
