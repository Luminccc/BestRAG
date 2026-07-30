"""QueryAnalyzer — 查询分析和意图识别。

分析 Query 类型，自动选择最佳检索策略。
"""

from typing import Any, Dict, List, Optional


class QueryIntent:
    """Query 分析结果。

    属性:
        type:             simple / multi_hop / technical / exact
        need_metadata:    是否需要元数据过滤
        retrieval_mode:   vector / bm25 / hybrid
        keywords:         提取的关键词
    """

    def __init__(
        self,
        query_type: str = "simple",
        need_metadata: bool = False,
        retrieval_mode: str = "vector",
        keywords: Optional[List[str]] = None,
        confidence: float = 1.0,
    ):
        self.type = query_type
        self.need_metadata = need_metadata
        self.retrieval_mode = retrieval_mode
        self.keywords = keywords or []
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "need_metadata": self.need_metadata,
            "retrieval_mode": self.retrieval_mode,
            "keywords": self.keywords,
            "confidence": self.confidence,
        }


class QueryAnalyzer:
    """查询分析器。

    识别 Query 类型并生成检索策略建议。
    """

    # 技术/操作类关键词（中英文）
    _TECHNICAL_KEYWORDS = [
        "configure", "deploy", "install", "setup", "api", "how to",
        "command", "error", "troubleshoot", "version", "upgrade",
        "config", "merge", "build", "debug", "compile",
        # 中文技术关键词
        "配置", "部署", "安装", "搭建", "设置", "错误", "故障",
        "升级", "迁移", "集成", "开发", "调试", "编译", "构建",
    ]

    # 精确查询模式（含引号或特定标识符）
    @staticmethod
    def analyze(query: str) -> QueryIntent:
        """分析 Query，返回意图。"""
        query_lower = query.lower().strip()

        if not query_lower:
            return QueryIntent(query_type="simple", retrieval_mode="vector")

        keywords = QueryAnalyzer._extract_keywords(query)

        # 精确查询（含引号或版本号）
        if '"' in query or "'" in query:
            return QueryIntent(query_type="exact", retrieval_mode="bm25", keywords=keywords)

        # 多跳查询（复杂关系/对比/长文本）
        if (len(query) > 50
                or any(w in query_lower for w in ["compare", "difference", "relationship"])):
            return QueryIntent(query_type="multi_hop", need_metadata=True, retrieval_mode="hybrid", keywords=keywords)

        # 技术查询
        if any(kw in query_lower for kw in QueryAnalyzer._TECHNICAL_KEYWORDS):
            return QueryIntent(
                query_type="technical",
                need_metadata=True,
                retrieval_mode="hybrid",
                keywords=keywords,
                confidence=0.8,
            )

        # 简单查询
        return QueryIntent(
            query_type="simple",
            retrieval_mode="vector",
            keywords=keywords,
        )

    @staticmethod
    def _extract_keywords(query: str) -> List[str]:
        """提取关键词（简单实现：过滤停用词）。"""
        stop_words = {"the", "a", "an", "is", "are", "was", "were",
                      "how", "what", "why", "where", "when", "which",
                      "to", "for", "in", "on", "at", "with", "by"}
        words = query.lower().split()
        return [w.strip(".,!?\"'") for w in words if w not in stop_words and len(w) > 2]
