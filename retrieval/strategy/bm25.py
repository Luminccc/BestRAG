"""BM25RetrievalStrategy — BM25 关键词检索策略。

封装现有的 BM25Retriever，继承 BaseRetrievalStrategy 接口。
"""

from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.strategy.retrieval import BaseRetrievalStrategy
from retrieval.retriever.bm25 import BM25Retriever
from retrieval.retriever.model import RetrievalResult

logger = get_logger(__name__)


class BM25RetrievalStrategy(BaseRetrievalStrategy):
    """BM25 关键词检索策略。"""

    name: str = "bm25"

    def __init__(self):
        self._bm25 = BM25Retriever()

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        results = self._bm25.retrieve(query, top_k, filters)
        logger.info(f"BM25RetrievalStrategy: {len(results)} 条结果")
        return results
