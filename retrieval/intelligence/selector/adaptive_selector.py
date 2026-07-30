"""AdaptiveRetrieverSelector — 自适应检索策略选择器。

根据 Query 类型、知识库特征和历史评测结果，自动选择最优检索配置。
"""

from typing import Any, Dict, Optional

from core.logger import get_logger
from core.models.retrieval import RetrievalProfile
from optimization.profile.model import RAGProfile
from retrieval.intelligence.query import QueryAnalyzer, QueryIntent

logger = get_logger("retrieval.selector")


class AdaptiveRetrieverSelector:
    """自适应检索选择器。

    根据 Query 类型自动选择最佳策略组合。
    """

    def __init__(self):
        self._query_analyzer = QueryAnalyzer()

    def select(self, query: str, kb_type: str = "") -> RetrievalProfile:
        """根据 Query 选择检索配置。"""
        intent = self._query_analyzer.analyze(query)
        return self._from_intent(intent, kb_type)

    def select_from_intent(self, intent: QueryIntent, kb_type: str = "") -> RetrievalProfile:
        """根据已分析的意图选择配置。"""
        return self._from_intent(intent, kb_type)

    def to_rag_profile(self, rp: RetrievalProfile) -> RAGProfile:
        """转为 v0.2 RAGProfile 兼容格式。"""
        return RAGProfile(
            name=rp.name,
            retrieval_strategies=list(rp.retrievers),
            fusion_strategy=rp.fusion,
            reranker=rp.reranker,
        )

    # ── 内部规则引擎 ──────────────────────────────

    def _from_intent(self, intent: QueryIntent, kb_type: str) -> RetrievalProfile:
        """根据意图生成检索配置。"""
        profile = RetrievalProfile(name="adaptive")

        if intent.type == "exact":
            profile.retrievers = ["bm25"]
            profile.fusion = "rrf"
            profile.top_k = 5

        elif intent.type == "technical":
            profile.retrievers = ["vector", "bm25"]
            profile.fusion = "rrf"
            profile.reranker = "bge"
            profile.top_k = 10

        elif intent.type == "multi_hop":
            profile.retrievers = ["vector", "bm25"]
            profile.fusion = "weighted"
            profile.reranker = "bge"
            profile.top_k = 15

        else:  # simple
            if kb_type == "faq":
                profile.retrievers = ["bm25"]
                profile.fusion = "rrf"
                profile.top_k = 5
            else:
                profile.retrievers = ["vector"]
                profile.fusion = "rrf"
                profile.top_k = 10

        profile.name = f"adaptive_{intent.type}"
        logger.info(f"自适应选择: type={intent.type}, retrievers={profile.retrievers}")
        return profile
