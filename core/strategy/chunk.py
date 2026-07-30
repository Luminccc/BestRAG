"""BaseChunkStrategy — 文档切分策略接口。

定义 Chunk 切分的统一契约，所有切分策略（Fixed/Recursive/Semantic/Heading 等）
必须实现 split 方法。

execute 委托给 split，保持与 BaseStrategy 兼容。
"""

from abc import abstractmethod
from typing import Any, List

from core.strategy.base import BaseStrategy


class BaseChunkStrategy(BaseStrategy):
    """Chunk 切分策略基类。"""

    name: str = "base_chunk"

    @abstractmethod
    def split(self, text: str, document_id: str) -> List[Any]:
        """将文本切分为 Chunk 对象列表。

        Args:
            text: 清洗后的文档文本内容。
            document_id: 来源 Document 的 ID。

        Returns:
            Chunk 对象列表。
        """

    def execute(self, text: str, document_id: str) -> List[Any]:
        """委托给 split。"""
        return self.split(text, document_id)
