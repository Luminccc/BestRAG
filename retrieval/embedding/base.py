"""BaseEmbedding — Embedding 模块基础接口。

定义：
- 文本转向量的基础接口
- 批量处理接口
"""

from abc import ABC, abstractmethod
from typing import List, Union

from core.exception import EmbeddingException


class BaseEmbedding(ABC):
    """Embedding 基础接口类。

    职责：
    - 将文本转换为向量表示
    - 支持单条文本和批量文本处理

    不负责：
    - 向量存储
    - 查询
    - 排序
    """

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """将单条文本转换为向量。

        Args:
            text: 输入文本

        Returns:
            文本的向量表示

        Raises:
            EmbeddingException: Embedding 过程中出现错误
        """
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """将多条文本转换为向量。

        Args:
            texts: 输入文本列表

        Returns:
            文本的向量表示列表

        Raises:
            EmbeddingException: Embedding 过程中出现错误
        """
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """获取向量维度。"""
        pass