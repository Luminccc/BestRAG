"""BGEM3 Rerank Provider — 基于 BGE M3 模型的 Rerank 实现。

使用 FlagEmbedding 库实现。
"""

from typing import List

from retrieval.reranker.base import BaseReranker
from retrieval.retriever.model import RetrievalResult
from core.exception import RerankException
from core.logger import get_logger

logger = get_logger(__name__)


class BGEReranker(BaseReranker):
    """BGE Rerank 实现。"""

    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        """初始化 BGE Rerank。

        Args:
            model_name: 模型名称
        """
        self._model_name = model_name
        self._model = None

    @property
    def model(self):
        """延迟加载 Rerank 模型（首次使用时才下载）。"""
        if self._model is None:
            try:
                from FlagEmbedding import FlagReranker
                self._model = FlagReranker(model_name_or_path=self._model_name)
                logger.info(f"BGE Rerank model loaded: {self._model_name}")
            except ImportError:
                raise RerankException(
                    "FlagEmbedding not installed. Please install it with: pip install FlagEmbedding"
                )
            except Exception as e:
                raise RerankException(f"Failed to load BGE rerank model: {str(e)}")
        return self._model

    def rerank(self, query: str, documents: List[RetrievalResult]) -> List[RetrievalResult]:
        """对文档列表进行重排序。

        Args:
            query: 查询文本
            documents: 待排序的文档列表

        Returns:
            重排序后的文档列表
        """
        if not query or not query.strip():
            raise RerankException("Query is empty")

        if not documents:
            return []

        try:
            # 准备数据进行重排序
            pairs = [(query, doc.content) for doc in documents]

            # 执行重排序得分计算
            scores = self.model.compute_score(pairs)

            # 如果只有一个分数，转换为列表
            if not isinstance(scores, list):
                scores = [scores]

            # 将分数与原始文档关联
            scored_docs = [(doc, score) for doc, score in zip(documents, scores)]

            # 按分数降序排序
            sorted_docs = sorted(scored_docs, key=lambda x: x[1], reverse=True)

            # 更新文档的分数并返回
            result = []
            for doc, score in sorted_docs:
                # 创建新对象，更新分数为重排序后的分数
                updated_doc = RetrievalResult(
                    chunk_id=doc.chunk_id,
                    score=float(score),
                    content=doc.content,
                    metadata=doc.metadata
                )
                result.append(updated_doc)

            return result
        except Exception as e:
            raise RerankException(f"Failed to rerank documents: {str(e)}")