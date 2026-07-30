"""BaseEmbeddingProvider — Embedding Provider 抽象。

负责将文本转换为向量表示。

实现（未来）：
- BGEEmbeddingProvider
- OpenAIEmbeddingProvider
- LocalEmbeddingProvider
"""

from abc import abstractmethod
from typing import List

from core.provider.base import BaseProvider


class BaseEmbeddingProvider(BaseProvider):
    """Embedding Provider 基类。"""

    name: str = "base_embedding"

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """将文本列表转换为向量。

        Args:
            texts: 输入文本列表。

        Returns:
            向量列表，每个文本对应一个向量。

        Raises:
            EmbeddingException: Embedding 过程出错。
        """

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """将单条文本转换为向量。

        Args:
            text: 输入文本。

        Returns:
            文本的向量表示。
        """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """向量维度。"""

    def execute(self, texts: List[str]) -> List[List[float]]:
        """委托给 embed。"""
        return self.embed(texts)
