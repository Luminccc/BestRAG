"""MetadataRetrievalStrategy — 元数据检索策略。

先通过元数据过滤缩小范围，再执行向量检索。
支持基于文档属性（年份、类别、部门等）的精确过滤。
"""

from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.strategy.retrieval import BaseRetrievalStrategy
from retrieval.retriever.model import RetrievalResult

logger = get_logger(__name__)


class MetadataRetrievalStrategy(BaseRetrievalStrategy):
    """元数据检索策略 — 过滤 + 向量搜索。"""

    name: str = "metadata"

    def __init__(self):
        from retrieval.strategy.vector import VectorRetrievalStrategy
        self._vector = VectorRetrievalStrategy()

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        # 提取元数据过滤条件
        meta_filters = kwargs.get("meta_filters", filters or {})

        # 执行带过滤的向量检索
        results = self._vector.retrieve(query, top_k, filters=meta_filters)

        # 标记策略
        for r in results:
            r.metadata["retrieval_strategy"] = "metadata"

        logger.info(f"MetadataRetrievalStrategy: {len(results)} 条结果 (filter={meta_filters})")
        return results
