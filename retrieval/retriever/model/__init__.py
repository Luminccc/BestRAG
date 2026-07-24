"""Retrieval 模型定义。

定义：
- RetrievalResult: 检索结果
- RetrievalQuery: 检索查询参数
"""

from typing import List, Dict, Any
from pydantic import BaseModel


class RetrievalResult(BaseModel):
    """检索结果。

    Attributes:
        chunk_id: Chunk ID
        score: 相似度分数
        content: Chunk 内容
        metadata: 元数据
    """
    chunk_id: str
    score: float
    content: str
    metadata: Dict[str, Any]


class RetrievalQuery(BaseModel):
    """检索查询参数。

    Attributes:
        query: 查询文本
        top_k: 返回结果数量
        filters: 过滤条件
        rerank: 是否需要重排序
    """
    query: str
    top_k: int = 10
    filters: Dict[str, Any] = {}
    rerank: bool = False