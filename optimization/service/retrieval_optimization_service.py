"""RetrievalOptimizationService — 检索优化服务。

提供 Dashboard API：
- analyze_query()
- recommend_strategy()
- get_quality_report()
- optimize_profile()
"""

from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.models.retrieval import RetrievalAnalysis, RetrievalProfile
from knowledge.intelligence import KnowledgeAnalyzer
from optimization.feedback import FeedbackAnalyzer
from optimization.optimizer.optimizer import RetrievalOptimizer
from optimization.profile.model import RAGProfile
from optimization.profile.registry import ProfileRegistry
from retrieval.intelligence import AdaptiveRetrieverSelector, QueryAnalyzer
from trace.storage import MemoryTraceStorage

logger = get_logger("optimization.service")


class RetrievalOptimizationService:
    """检索优化服务。

    Dashboard API 入口。
    """

    def __init__(self):
        self._query_analyzer = QueryAnalyzer()
        self._selector = AdaptiveRetrieverSelector()
        self._knowledge = KnowledgeAnalyzer()
        self._feedback = FeedbackAnalyzer()
        self._optimizer = RetrievalOptimizer()
        self._profile_registry = ProfileRegistry()

    def analyze_query(self, query: str) -> Dict[str, Any]:
        """分析 Query，返回意图和推荐策略。"""
        intent = self._query_analyzer.analyze(query)
        profile = self._selector.select(query)
        return {
            "query": query,
            "intent": intent.to_dict(),
            "recommended_profile": profile.to_dict(),
        }

    def recommend_strategy(self, query: str, kb_type: str = "") -> Dict[str, Any]:
        """推荐检索策略。"""
        intent = self._query_analyzer.analyze(query)
        profile = self._selector.select(query, kb_type)
        rag_profile = self._selector.to_rag_profile(profile)
        return {
            "query": query,
            "intent": intent.type,
            "retrievers": profile.retrievers,
            "fusion": profile.fusion,
            "reranker": profile.reranker,
            "top_k": profile.top_k,
        }

    def get_quality_report(self) -> Dict[str, Any]:
        """获取检索质量报告。"""
        failures = self._feedback.collect_failures(limit=20)
        suggestions = self._feedback.generate_suggestions(limit=20)

        return {
            "total_failures": len(failures),
            "recent_failures": failures[:5],
            "suggestions": [
                {"type": s.suggestion_type, "reason": s.reason}
                for s in suggestions[:5]
            ],
        }

    def optimize_profile(
        self,
        profile_name: str = "default",
    ) -> Dict[str, Any]:
        """获取 Profile 优化建议。"""
        profile = self._profile_registry.get(profile_name)
        if profile is None:
            return {"error": f"Profile '{profile_name}' 不存在"}

        alternatives = {
            "chunk_strategy": ["recursive", "semantic", "hierarchical"],
            "fusion": ["rrf", "weighted"],
        }

        all_suggestions = []
        for component, alt_list in alternatives.items():
            current = getattr(profile, component, "")
            suggestions = self._optimizer.optimize_component(component, current, alt_list)
            all_suggestions.extend(s.to_dict() for s in suggestions)

        return {
            "profile": profile.to_dict(),
            "optimization_suggestions": all_suggestions,
        }
