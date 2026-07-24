"""RerankService — Rerank 模块服务层。

负责：
- Rerank 实例管理
- Rerank 流程编排
"""

from typing import List, Optional

from retrieval.reranker.base import BaseReranker
from retrieval.reranker.providers.bge import BGEReranker
from retrieval.reranker.providers.bge_api import BGEAPIReranker
from retrieval.retriever.model import RetrievalResult
from core.config import get_config
from core.registry import get_service, register_service_factory
from core.logger import get_logger
from core.exception import RerankException

logger = get_logger(__name__)


class RerankService:
    """Rerank 服务类。

    职责：
    - 管理 Rerank 实例
    - 提供统一的 Rerank 接口
    """

    def __init__(self, reranker: Optional[BaseReranker] = None):
        """初始化 Rerank 服务。

        Args:
            reranker: Rerank 实例，如果为 None 则根据配置创建默认实例
        """
        if reranker is None:
            # 根据配置创建默认 Rerank 实例
            config = get_config().retrieval
            # 优先使用 API 模式（BGE-Rerank Docker 服务）
            if config.rerank_api_url:
                self._reranker = BGEAPIReranker(config.rerank_api_url)
            elif config.rerank_model.startswith("BAAI/bge"):
                self._reranker = BGEReranker(config.rerank_model)
            else:
                # 默认使用 BGE 模型
                self._reranker = BGEReranker()
        else:
            self._reranker = reranker

    def rerank(self, query: str, documents: List[RetrievalResult]) -> List[RetrievalResult]:
        """对文档列表进行重排序。

        Args:
            query: 查询文本
            documents: 待排序的文档列表

        Returns:
            重排序后的文档列表
        """
        logger.info("Reranking documents", query=query[:50] + "..." if len(query) > 50 else query, count=len(documents))

        return self._reranker.rerank(query, documents)


def _create_rerank_service() -> RerankService:
    """创建 Rerank 服务实例。"""
    return RerankService()


# 注册服务工厂
register_service_factory("rerank", _create_rerank_service)


def get_rerank_service() -> RerankService:
    """获取 Rerank 服务实例。"""
    return get_service("rerank", RerankService)