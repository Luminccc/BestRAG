"""BaseFusionStrategy — 融合策略基类。

所有融合策略继承此基类，统一 fuse 接口。
"""

from abc import abstractmethod
from typing import Any, List

from core.strategy.base import BaseStrategy


class BaseFusionStrategy(BaseStrategy):
    """融合策略基类。"""

    name: str = "base_fusion"

    @abstractmethod
    def fuse(self, results: List[List[Any]], **kwargs: Any) -> List[Any]:
        """融合多路召回结果。

        Args:
            results: 多路检索结果，每个元素是一路结果列表。
            **kwargs: 融合参数（权重等）。

        Returns:
            融合排序后的结果列表。
        """

    def execute(self, results: List[List[Any]], **kwargs: Any) -> List[Any]:
        return self.fuse(results, **kwargs)
