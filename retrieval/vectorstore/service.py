"""VectorStoreService — VectorStore 模块服务层。

负责：
- VectorStore 实例管理（延迟初始化）
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
    """VectorStore 服务类。使用延迟初始化，首次调用时连接 Milvus。"""

    def __init__(self, vector_store: Optional[BaseVectorStore] = None):
        self._vector_store = vector_store  # None = 延迟初始化

    def _ensure_store(self):
        """延迟初始化 VectorStore 实例。"""
        if self._vector_store is not None:
            return
        config = get_config().vectorstore
        try:
            self._vector_store = MilvusVectorStore()
        except Exception as e:
            raise VectorStoreException(f"VectorStore 初始化失败: {e}") from e

    def add(
        self, vectors: List[List[float]], texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """写入向量到存储（Indexing 模块使用的接口名）。"""
        return self.add_texts(texts, vectors, metadatas, ids)

    def add(
        self, vectors: List[List[float]], texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """写入向量到 VectorStore（Indexing 模块使用的接口）。"""
        return self.add_texts(texts, vectors, metadatas, ids)

    def add_texts(
        self, texts: List[str], embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        self._ensure_store()
        if ids is None:
            ids = [str(uuid4()) for _ in texts]
        return self._vector_store.add(embeddings, texts, metadatas, ids)

    def similarity_search(
        self, query: str, query_embedding: List[float],
        top_k: int = 10, filters: Optional[Dict[str, Any]] = None,
    ) -> SearchResult:
        self._ensure_store()
        results = self._vector_store.search(query_embedding, top_k, filters)
        return SearchResult(
            results=[VectorStoreResult(id=r[0], score=r[1], content=r[2], metadata=r[3]) for r in results],
            query=query, top_k=top_k,
        )

    def delete(self, ids: List[str]) -> bool:
        self._ensure_store()
        return self._vector_store.delete(ids)

    def get_dimension(self) -> int:
        self._ensure_store()
        return self._vector_store.get_dimension()

    def close(self) -> None:
        if self._vector_store is not None:
            self._vector_store.close()

    def collection_info(self) -> Optional[str]:
        """获取 collection 状态信息（用于状态检查）。"""
        try:
            self._ensure_store()
            return "connected"
        except Exception as e:
            return None


def _create_vector_store_service() -> VectorStoreService:
    return VectorStoreService()


register_service_factory("vector_store", _create_vector_store_service)


def get_vector_store_service() -> VectorStoreService:
    return get_service("vector_store", VectorStoreService)
