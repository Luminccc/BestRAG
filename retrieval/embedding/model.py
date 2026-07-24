"""Embedding 模型定义。

定义：
- EmbeddingResult: 单条文本的 Embedding 结果
"""

from typing import List
from pydantic import BaseModel


class EmbeddingResult(BaseModel):
    """Embedding 结果。

    Attributes:
        text: 原始文本
        vector: 文本的向量表示
        dimension: 向量维度
    """
    text: str
    vector: List[float]
    dimension: int