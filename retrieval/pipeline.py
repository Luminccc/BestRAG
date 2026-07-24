"""Pipeline — Retrieval 流程编排。

负责：
- 整合 Embedding、VectorStore、Retrieval 和 Rerank 模块
- 执行完整的检索流程
"""

from typing import List, Optional

from retrieval.embedding.service import EmbeddingService, get_embedding_service
from retrieval.vectorstore.service import VectorStoreService, get_vector_store_service
from retrieval.retriever.service import RetrievalService, get_retrieval_service
from retrieval.reranker.service import RerankService, get_rerank_service
from retrieval.retriever.model import RetrievalResult
from core.logger import get_logger

logger = get_logger(__name__)


class RetrievalPipeline:
    """Retrieval 流程编排类。

    职责：
    - 协调所有 Retrieval 模块
    - 执行完整的检索流程
    """

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store_service: Optional[VectorStoreService] = None,
        retrieval_service: Optional[RetrievalService] = None,
        rerank_service: Optional[RerankService] = None
    ):
        """初始化 Retrieval 流程。

        Args:
            embedding_service: Embedding 服务
            vector_store_service: VectorStore 服务
            retrieval_service: Retrieval 服务
            rerank_service: Rerank 服务
        """
        self._embedding_service = embedding_service or get_embedding_service()
        self._vector_store_service = vector_store_service or get_vector_store_service()
        self._retrieval_service = retrieval_service or get_retrieval_service()
        self._rerank_service = rerank_service or get_rerank_service()

    def retrieve(self, query: str, top_k: int = 10, use_rerank: bool = False) -> List[RetrievalResult]:
        """执行完整的检索流程。

        Args:
            query: 查询文本
            top_k: 返回结果数量
            use_rerank: 是否使用重排序

        Returns:
            检索结果列表
        """
        logger.info("Starting retrieval pipeline", query=query[:50] + "..." if len(query) > 50 else query, top_k=top_k)

        # 1. 执行检索
        results = self._retrieval_service.retrieve(query, top_k)

        # 2. 如果需要，执行重排序
        if use_rerank and len(results) > 0:
            logger.info("Applying rerank", count=len(results))
            results = self._rerank_service.rerank(query, results)

        logger.info(f"Retrieval pipeline completed, returning {len(results)} results")
        return results


def get_pipeline() -> RetrievalPipeline:
    """获取 Retrieval 流程实例。"""
    return RetrievalPipeline()