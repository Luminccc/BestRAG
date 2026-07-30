"""BaseRetrievalStrategy — 检索策略接口。

定义检索的统一契约，所有检索策略（Vector/BM25/Hybrid/Context/Hierarchical）
必须实现 retrieve 方法。

execute 委托给 retrieve，保持与 BaseStrategy 兼容。
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional


from core.strategy.base import BaseStrategy


class BaseRetrievalStrategy(BaseStrategy):
    """检索策略基类。"""

    name: str = "base_retrieval"

    @abstractmethod
    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        **kwargs: Any,
    ) -> List[Any]:
        """执行检索。

        Args:
            query: 查询文本。
            top_k: 返回结果数量。
            **kwargs: 扩展参数（filter、rerank 等）。

        Returns:
            检索结果列表。
        """

    def execute(self, query: str, top_k: int = 10, **kwargs: Any) -> List[Any]:
        """委托给 retrieve。"""
        return self.retrieve(query, top_k, **kwargs)
