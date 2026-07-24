"""VectorStore 模型定义。

定义：
- VectorStoreResult: 单条搜索结果
- SearchResult: 搜索结果集合
"""

from typing import List, Dict, Any
from pydantic import BaseModel


class VectorStoreResult(BaseModel):
    """向量存储结果。

    Attributes:
        id: 向量 ID
        score: 相似度分数
        content: 原始文本内容
        metadata: 元数据
    """
    id: str
    score: float
    content: str
    metadata: Dict[str, Any]


class SearchResult(BaseModel):
    """搜索结果集合。

    Attributes:
        results: 搜索结果列表
        query: 查询文本
        top_k: 请求返回数量
    """
    results: List[VectorStoreResult]
    query: str
    top_k: int