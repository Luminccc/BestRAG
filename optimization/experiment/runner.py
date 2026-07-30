"""ExperimentRunner — 实验批量运行器。

对多个 Profile 执行实验，输出评测结果。
"""

from typing import Callable, Dict, List, Optional

from evaluation.benchmark.dataset import EvaluationDataset
from evaluation.service.evaluation_service import EvaluationService
from optimization.experiment.experiment import Experiment
from optimization.profile.model import RAGProfile
from optimization.profile.registry import ProfileRegistry


class ExperimentRunner:
    """实验运行器。

    用法::

        runner = ExperimentRunner(dataset, retrieve_fn)
        experiments = runner.run_all(registry.list())
    """

    def __init__(
        self,
        dataset: EvaluationDataset,
        retrieve_fn: Callable,
        k: int = 5,
    ):
        self._dataset = dataset
        self._retrieve_fn = retrieve_fn
        self._k = k
        self._eval_svc = EvaluationService()

    def run(self, profile: RAGProfile) -> Experiment:
        """运行单个 Profile 实验。"""
        # 包装检索函数，使 Profile 生效
        def wrapped_fn(query: str, top_k: int = 10, **kwargs):
            return self._retrieve_fn(
                query, top_k=top_k,
                strategies=profile.retrieval_strategies,
                **kwargs,
            )

        report = self._eval_svc.benchmark(
            dataset=self._dataset,
            retrieve_fn=wrapped_fn,
            strategy_profile=profile.to_dict(),
            scenario=profile.name,
            k=self._k,
        )
        return Experiment(
            name=profile.name,
            dataset=self._dataset,
            profile=profile,
            retrieve_fn=self._retrieve_fn,
            k=self._k,
            result=report,
        )

    def run_all(self, profiles: List[RAGProfile]) -> List[Experiment]:
        """批量运行多个 Profile 实验。"""
        return [self.run(p) for p in profiles]
