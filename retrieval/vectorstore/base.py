"""BaseVectorStore — VectorStore 模块基础接口。

定义：
- 向量存储和检索的基础接口
- 数据添加、删除、搜索功能
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from core.exception import VectorStoreException


class BaseVectorStore(ABC):
    """VectorStore 基础接口类。

    职责：
    - 保存向量
    - 删除向量
    - 相似度搜索

    不负责：
    - 文本处理
    - Embedding
    """

    @abstractmethod
    def add(
        self,
        vectors: List[List[float]],
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """添加向量到存储。

        Args:
            vectors: 向量列表
            texts: 文本列表
            metadatas: 元数据列表
            ids: ID 列表，如果为 None 则自动生成

        Returns:
            添加成功的 ID 列表

        Raises:
            VectorStoreException: 添加过程中出现错误
        """
        pass

    @abstractmethod
    def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, str, Dict[str, Any]]]:
        """搜索相似向量。

        Args:
            query_vector: 查询向量
            top_k: 返回结果数量
            filters: 过滤条件

        Returns:
            包含 (ID, 相似度分数, 文本, 元数据) 的元组列表

        Raises:
            VectorStoreException: 搜索过程中出现错误
        """
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> bool:
        """删除向量。

        Args:
            ids: 要删除的 ID 列表

        Returns:
            删除是否成功

        Raises:
            VectorStoreException: 删除过程中出现错误
        """
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """获取向量维度。"""
        pass

    @abstractmethod
    def close(self) -> None:
        """关闭连接。"""
        pass