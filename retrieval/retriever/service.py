"""RetrievalService — Retrieval 模块服务层。

负责：
- 检索流程编排
- Embedding 和 VectorStore 的协调
- 检索结果处理
"""

from typing import List, Optional

from retrieval.retriever.model import RetrievalResult, RetrievalQuery
from retrieval.embedding.service import EmbeddingService, get_embedding_service
from retrieval.vectorstore.service import VectorStoreService, get_vector_store_service
from core.registry import get_service, register_service_factory
from core.logger import get_logger
from core.exception import RetrievalException

logger = get_logger(__name__)


class RetrievalService:
    """Retrieval 服务类。

    职责：
    - 协调 Embedding 和 VectorStore 服务
    - 执行检索流程
    - 返回检索结果
    """

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store_service: Optional[VectorStoreService] = None
    ):
        """初始化 Retrieval 服务。

        Args:
            embedding_service: Embedding 服务实例
            vector_store_service: VectorStore 服务实例
        """
        self._embedding_service = embedding_service or get_embedding_service()
        self._vector_store_service = vector_store_service or get_vector_store_service()

    def retrieve(self, query: str, top_k: int = 10) -> List[RetrievalResult]:
        """执行检索。

        Args:
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        logger.info("Starting retrieval", query=query[:50] + "..." if len(query) > 50 else query, top_k=top_k)

        try:
            # 1. Embedding 查询文本
            embedding_result = self._embedding_service.embed_text(query)
            query_vector = embedding_result.vector

            # 2. 在向量存储中搜索
            search_result = self._vector_store_service.similarity_search(
                query=query,
                query_embedding=query_vector,
                top_k=top_k
            )

            # 3. 转换结果格式
            results = [
                RetrievalResult(
                    chunk_id=vs_result.id,
                    score=vs_result.score,
                    content=vs_result.content,
                    metadata=vs_result.metadata
                )
                for vs_result in search_result.results
            ]

            logger.info(f"Retrieved {len(results)} results")
            return results

        except Exception as e:
            logger.error("Retrieval failed", error=str(e))
            raise RetrievalException(f"Retrieval failed: {str(e)}")


def _create_retrieval_service() -> RetrievalService:
    """创建 Retrieval 服务实例。"""
    return RetrievalService()


# 注册服务工厂
register_service_factory("retrieval", _create_retrieval_service)


def get_retrieval_service() -> RetrievalService:
    """获取 Retrieval 服务实例。"""
    return get_service("retrieval", RetrievalService)