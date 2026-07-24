"""BaseReranker — Rerank 模块基础接口。

定义：
- 重排序的基础接口
"""

from abc import ABC, abstractmethod
from typing import List

from retrieval.retriever.model import RetrievalResult
from core.exception import RerankException


class BaseReranker(ABC):
    """Rerank 基础接口类。

    职责：
    - 对检索结果进行重排序
    - 提升相关结果的排名
    """

    @abstractmethod
    def rerank(self, query: str, documents: List[RetrievalResult]) -> List[RetrievalResult]:
        """对文档列表进行重排序。

        Args:
            query: 查询文本
            documents: 待排序的文档列表

        Returns:
            重排序后的文档列表

        Raises:
            RerankException: 重排序过程中出现错误
        """
        pass