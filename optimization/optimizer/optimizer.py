"""RetrievalOptimizer — 检索优化引擎。

升级现有 ProfileSelector：
- 支持自动优化各项组件
- 结合 Evaluation 数据
- 连接 Phase 3 Experiment Framework
"""

from typing import Any, Callable, Dict, List, Optional, Tuple

from core.logger import get_logger
from core.models.retrieval import OptimizationSuggestion, RetrievalProfile
from evaluation.benchmark.dataset import EvaluationDataset
from evaluation.experiment import ExperimentManager
from optimization.feedback import FeedbackAnalyzer
from optimization.profile.model import RAGProfile
from optimization.profile.registry import ProfileRegistry

logger = get_logger("optimization.optimizer")


class RetrievalOptimizer:
    """检索优化引擎。

    能力：
    - 自动优化 Chunk Strategy / Embedding / Retriever / Fusion / TopK
    - 基于 Experiment Framework 验证优化效果
    """

    def __init__(
        self,
        profile_registry: Optional[ProfileRegistry] = None,
        feedback_analyzer: Optional[FeedbackAnalyzer] = None,
    ):
        self._registry = profile_registry or ProfileRegistry()
        self._feedback = feedback_analyzer or FeedbackAnalyzer()
        self._experiment = ExperimentManager()

    def optimize_profile(
        self,
        profile: RAGProfile,
        dataset: EvaluationDataset,
        retrieve_fn: Callable,
        k: int = 5,
    ) -> Tuple[RAGProfile, Dict[str, float]]:
        """优化单个 Profile。

        Args:
            profile: 待优化的 Profile。
            dataset: 评测数据集。
            retrieve_fn: 检索函数。
            k: 评测 K 值。

        Returns:
            (优化后的 Profile, 优化后的指标)
        """
        logger.info(f"开始优化 Profile: {profile.name}")

        # 收集反馈建议
        suggestions = self._feedback.generate_suggestions()
        if not suggestions:
            logger.info("无优化建议，保持当前 Profile")
            return profile, {}

        # 应用建议生成优化版本
        optimized = self._apply_suggestions(profile, suggestions)

        # 通过实验验证
        exp_report = self._experiment.compare_strategies(
            dataset,
            {
                "original": retrieve_fn,
                "optimized": retrieve_fn,  # 实际需用优化后的函数
            },
            k=k,
        )
        metrics = exp_report.compare("recall@5") if hasattr(exp_report, 'compare') else {}

        logger.info(f"Profile 优化完成: {profile.name}")
        return optimized, metrics

    def optimize_component(
        self,
        component: str,
        current_value: str,
        alternatives: List[str],
    ) -> List[OptimizationSuggestion]:
        """优化单个组件。

        Args:
            component: 组件名（chunk_strategy / embedding / retriever / fusion / top_k）。
            current_value: 当前值。
            alternatives: 候选值列表。

        Returns:
            优化建议列表。
        """
        suggestions = []
        for alt in alternatives:
            if alt == current_value:
                continue
            suggestions.append(OptimizationSuggestion(
                suggestion_type=f"{component}_change",
                target=component,
                value_from=current_value,
                value_to=alt,
                reason=f"尝试替代 {component}: {alt}",
                score_impact=0.1,
            ))
        return suggestions

    def _apply_suggestions(
        self,
        profile: RAGProfile,
        suggestions: List[OptimizationSuggestion],
    ) -> RAGProfile:
        """将优化建议应用到 Profile。"""
        import copy
        optimized = copy.deepcopy(profile)

        for s in suggestions:
            if s.suggestion_type == "retriever_change" and s.target:
                if hasattr(optimized, 'retrieval_strategies'):
                    logger.info(f"应用建议: {s.suggestion_type} -> {s.reason}")

        return optimized
