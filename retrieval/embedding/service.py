"""EmbeddingService — Embedding 模块服务层。

负责：
- Embedding 实例管理
- Embedding 流程编排
"""

from typing import List, Optional

from retrieval.embedding.base import BaseEmbedding
from retrieval.embedding.providers.bge import BGEEmbedding
from retrieval.embedding.providers.bge_api import BGEAPIEmbedding
from retrieval.embedding.model import EmbeddingResult
from core.config import get_config
from core.registry import get_service, register_service_factory
from core.logger import get_logger
from core.exception import EmbeddingException

logger = get_logger(__name__)


class EmbeddingService:
    """Embedding 服务类。

    职责：
    - 管理 Embedding 实例
    - 提供统一的 Embedding 接口
    """

    def __init__(self, embedding: Optional[BaseEmbedding] = None):
        """初始化 Embedding 服务。

        Args:
            embedding: Embedding 实例，如果为 None 则根据配置创建默认实例
        """
        if embedding is None:
            # 根据配置创建默认 Embedding 实例
            config = get_config().retrieval
            # 优先使用 API 模式（BGE-M3 Docker 服务）
            if config.embedding_api_url:
                self._embedding = BGEAPIEmbedding(config.embedding_api_url)
            elif config.embedding_model.startswith("BAAI/bge"):
                self._embedding = BGEEmbedding(config.embedding_model)
            else:
                # 默认使用 BGE 模型
                self._embedding = BGEEmbedding()
        else:
            self._embedding = embedding

    def embed_text(self, text: str) -> EmbeddingResult:
        """将单条文本转换为向量。

        Args:
            text: 输入文本

        Returns:
            Embedding 结果
        """
        logger.info("Embedding single text", text=text[:50] + "..." if len(text) > 50 else text)

        vector = self._embedding.embed_text(text)

        return EmbeddingResult(
            text=text,
            vector=vector,
            dimension=self._embedding.dimension
        )

    def embed_documents(self, texts: List[str]) -> List[EmbeddingResult]:
        """将多条文本转换为向量。

        Args:
            texts: 输入文本列表

        Returns:
            Embedding 结果列表
        """
        logger.info("Embedding documents", count=len(texts))

        vectors = self._embedding.embed_documents(texts)

        results = []
        for text, vector in zip(texts, vectors):
            results.append(EmbeddingResult(
                text=text,
                vector=vector,
                dimension=self._embedding.dimension
            ))

        return results

    @property
    def dimension(self) -> int:
        """获取向量维度。"""
        return self._embedding.dimension


def _create_embedding_service() -> EmbeddingService:
    """创建 Embedding 服务实例。"""
    return EmbeddingService()


# 注册服务工厂
register_service_factory("embedding", _create_embedding_service)


def get_embedding_service() -> EmbeddingService:
    """获取 Embedding 服务实例。"""
    return get_service("embedding", EmbeddingService)