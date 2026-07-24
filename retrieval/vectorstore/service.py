"""VectorStoreService — VectorStore 模块服务层。

负责：
- VectorStore 实例管理
- VectorStore 流程编排
"""

from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from retrieval.vectorstore.base import BaseVectorStore
from retrieval.vectorstore.providers.milvus import MilvusVectorStore
from retrieval.vectorstore.model import VectorStoreResult, SearchResult
from core.config import get_config
from core.registry import get_service, register_service_factory
from core.logger import get_logger
from core.exception import VectorStoreException

logger = get_logger(__name__)


class VectorStoreService:
    """VectorStore 服务类。

    职责：
    - 管理 VectorStore 实例
    - 提供统一的 VectorStore 接口
    """

    def __init__(self, vector_store: Optional[BaseVectorStore] = None):
        """初始化 VectorStore 服务。

        Args:
            vector_store: VectorStore 实例，如果为 None 则根据配置创建默认实例
        """
        if vector_store is None:
            # 根据配置创建默认 VectorStore 实例
            config = get_config().retrieval
            if config.vectorstore_type == "milvus":
                self._vector_store = MilvusVectorStore()
            else:
                # 默认使用 Milvus
                self._vector_store = MilvusVectorStore()
        else:
            self._vector_store = vector_store

    def add_texts(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """添加文本及其向量表示到存储。

        Args:
            texts: 文本列表
            embeddings: 向量表示列表
            metadatas: 元数据列表
            ids: ID 列表，如果为 None 则自动生成

        Returns:
            添加成功的 ID 列表
        """
        logger.info("Adding texts to vector store", count=len(texts))

        # 生成 ID（如果未提供）
        if ids is None:
            ids = [str(uuid4()) for _ in texts]

        # 添加到向量存储
        result_ids = self._vector_store.add(embeddings, texts, metadatas, ids)

        return result_ids

    def similarity_search(
        self,
        query: str,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> SearchResult:
        """相似度搜索。

        Args:
            query: 查询文本
            query_embedding: 查询向量
            top_k: 返回结果数量
            filters: 过滤条件

        Returns:
            搜索结果
        """
        logger.info("Performing similarity search", query=query[:50] + "..." if len(query) > 50 else query, top_k=top_k)

        # 执行搜索
        results = self._vector_store.search(query_embedding, top_k, filters)

        # 转换为 VectorStoreResult 对象
        vector_results = [
            VectorStoreResult(
                id=result[0],
                score=result[1],
                content=result[2],
                metadata=result[3]
            )
            for result in results
        ]

        return SearchResult(
            results=vector_results,
            query=query,
            top_k=top_k
        )

    def delete(self, ids: List[str]) -> bool:
        """删除向量。

        Args:
            ids: 要删除的 ID 列表

        Returns:
            删除是否成功
        """
        logger.info("Deleting vectors from vector store", count=len(ids))

        return self._vector_store.delete(ids)

    def get_dimension(self) -> int:
        """获取向量维度。"""
        return self._vector_store.get_dimension()

    def close(self) -> None:
        """关闭连接。"""
        self._vector_store.close()


def _create_vector_store_service() -> VectorStoreService:
    """创建 VectorStore 服务实例。"""
    return VectorStoreService()


# 注册服务工厂
register_service_factory("vector_store", _create_vector_store_service)


def get_vector_store_service() -> VectorStoreService:
    """获取 VectorStore 服务实例。"""
    return get_service("vector_store", VectorStoreService)