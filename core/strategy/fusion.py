"""BaseFusionStrategy — 多路召回融合策略接口。

定义 Fusion 的统一契约，所有融合策略（Weighted/RRF/Dynamic）
必须实现 fuse 方法。

每个策略接收多个检索结果列表，输出一条融合排序后的结果列表。
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
            results: 多个检索结果列表，每个元素是一个 RetrievalResult 列表。
            **kwargs: 扩展参数（权重等）。

        Returns:
            融合排序后的结果列表。
        """

    def execute(self, results: List[List[Any]], **kwargs: Any) -> List[Any]:
        """委托给 fuse。"""
        return self.fuse(results, **kwargs)
