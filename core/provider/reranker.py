"""BaseRerankerProvider — Reranker Provider 抽象。

负责对检索结果进行重排序。

实现（未来）：
- BGERerankerProvider
- CohereRerankerProvider
- CrossEncoderRerankerProvider
"""

from abc import abstractmethod
from typing import Any, List

from core.provider.base import BaseProvider


class BaseRerankerProvider(BaseProvider):
    """Reranker Provider 基类。"""

    name: str = "base_reranker"

    @abstractmethod
    def rerank(self, query: str, documents: List[Any]) -> List[Any]:
        """对文档列表进行重排序。

        Args:
            query: 查询文本。
            documents: 待排序的文档列表。

        Returns:
            重排序后的文档列表。
        """

    def execute(self, query: str, documents: List[Any]) -> List[Any]:
        """委托给 rerank。"""
        return self.rerank(query, documents)
