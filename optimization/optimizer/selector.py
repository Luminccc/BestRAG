"""ProfileSelector — 运行时 Profile 选择器。

根据知识库特征和可用的 Profile 推荐最佳配置。
"""

from typing import Any, Dict, List, Optional, Tuple

from optimization.experiment.experiment import Experiment
from optimization.optimizer.ranking import RankingEngine
from optimization.profile.model import RAGProfile
from optimization.profile.registry import ProfileRegistry


class ProfileSelector:
    """Profile 选择器。

    用法::

        selector = ProfileSelector(registry)
        best_profile = selector.select_for_knowledge_base(
            kb_metadata={"type": "technical", "language": "Chinese"}
        )
    """

    def __init__(self, registry: ProfileRegistry):
        self._registry = registry
        self._ranking = RankingEngine()

    def select_by_name(self, name: str) -> Optional[RAGProfile]:
        """按名称选择 Profile。"""
        return self._registry.get(name)

    def select_by_scenario(self, scenario: str) -> Optional[RAGProfile]:
        """按场景名选择 Profile。"""
        scenario_map = {
            "technical": "technical_doc",
            "faq": "faq",
            "long_doc": "long_doc",
            "paper": "paper",
        }
        name = scenario_map.get(scenario, "default")
        return self._registry.get(name)

    def select_for_knowledge_base(
        self,
        kb_metadata: Dict[str, Any],
    ) -> RAGProfile:
        """根据知识库元数据推荐 Profile。

        基于规则匹配：
        - 文档类型（technical/faq/paper）
        - 文档结构（markdown/pdf）
        - 文档规模
        """
        doc_type = str(kb_metadata.get("type", "")).lower()
        structure = str(kb_metadata.get("structure", "")).lower()
        doc_count = kb_metadata.get("doc_count", 0)

        # 规则匹配
        if "faq" in doc_type:
            return self._registry.get("faq") or self._registry.get("default")
        if "paper" in doc_type or "academic" in doc_type:
            return self._registry.get("paper") or self._registry.get("default")
        if "markdown" in structure or "technical" in doc_type:
            return self._registry.get("technical_doc") or self._registry.get("default")
        if doc_count > 1000 or "long" in doc_type:
            return self._registry.get("long_doc") or self._registry.get("default")

        return self._registry.get("default")

    def from_best_experiment(
        self,
        experiments: List[Experiment],
    ) -> Tuple[Optional[RAGProfile], float]:
        """从实验结果中选择最优 Profile。"""
        best_exp, score = self._ranking.get_best(experiments)
        if best_exp is None:
            return None, 0.0
        return best_exp.profile, score
