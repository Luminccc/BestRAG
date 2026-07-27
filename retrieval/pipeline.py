"""Retrieval Pipeline V2 — 增强检索流程编排。

完整链路::

    Query
      │
      ▼
    RetrievalCache   ←── index-aware key
      │ (miss)
      ▼
    EmbeddingCache   ←── Redis
      │ (miss)
      ▼
    ┌──────────────────────┐
    │  Vector + BM25       │  ←── strategy 选 hybrid/vector/bm25
    └──────────────────────┘
      │
      ▼
    Fusion             ←── weighted merge
      │
      ▼
    MetadataFilter     ←── filter conditions
      │
      ▼
    Reranker           ←── optional
      │
      ▼
    Result
"""

from typing import Any, Dict, List, Optional

from core.config import get_config
from core.logger import get_logger
from retrieval.cache.embedding_cache import EmbeddingCache
from retrieval.cache.retrieval_cache import RetrievalCache
from retrieval.filter.metadata import MetadataFilter
from retrieval.retriever.bm25 import BM25Retriever
from retrieval.retriever.hybrid import HybridRetriever
from retrieval.retriever.model import RetrievalResult
from retrieval.retriever.vector import VectorRetriever

logger = get_logger(__name__)

# Registry keys
_EMBEDDING_KEY = "embedding"
_RERANK_KEY = "rerank"


class RetrievalPipelineV2:
    """检索管线 V2 — 缓存 → 策略检索 → 融合 → 过滤 → 重排序。

    Usage::

        pipeline = RetrievalPipelineV2()
        results = pipeline.retrieve("如何部署?", top_k=10, filters={"department": "finance"})
    """

    def __init__(
        self,
        vector_retriever: Optional[VectorRetriever] = None,
        bm25_retriever: Optional[BM25Retriever] = None,
        hybrid_retriever: Optional[HybridRetriever] = None,
        metadata_filter: Optional[MetadataFilter] = None,
        embedding_cache: Optional[EmbeddingCache] = None,
        retrieval_cache: Optional[RetrievalCache] = None,
    ):
        self._vector = vector_retriever or VectorRetriever()
        self._bm25 = bm25_retriever or BM25Retriever()
        self._hybrid = hybrid_retriever or HybridRetriever(self._vector, self._bm25)
        self._filter = metadata_filter or MetadataFilter()
        self._emb_cache = embedding_cache or EmbeddingCache()
        self._ret_cache = retrieval_cache or RetrievalCache()

    # ── 主入口 ────────────────────────────────────

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        use_rerank: bool = True,
    ) -> List[RetrievalResult]:
        """执行完整的增强检索流程。

        Args:
            query:      查询文本。
            top_k:      返回结果数量。
            filters:    元数据过滤条件（如 {"department": "finance"}）。
            use_rerank: 是否启用重排序。

        Returns:
            检索结果列表。
        """
        cfg = get_config().retrieval
        strategy = cfg.strategy

        # Step 0: Retrieval Cache
        results = self._ret_cache.get(query, strategy, top_k, filters)
        if results is not None:
            logger.info(f"Retrieval cache HIT: {query[:50]}...")
            return results

        # Step 1: Embedding Cache（Vector 策略时预取 embedding）
        # 注：V2 embedding cache 在 VectorRetriever 内部调用前预填充
        # 当前 VectorRetriever 直接调用 embedding service，cache 由它自行使用

        # Step 2: 策略检索
        results = self._execute_strategy(query, top_k, filters, strategy)

        # Step 3: Metadata Filter
        if filters and cfg.filter_enabled:
            results = self._filter.filter(results, filters)

        # Step 4: Reranker
        if use_rerank and results:
            try:
                reranker = self._get_reranker()
                if reranker:
                    results = reranker.rerank(query, results)
            except Exception as e:
                logger.warning(f"Reranker 调用失败，跳过: {e}")

        # Step 5: 缓存结果
        self._ret_cache.set(query, strategy, top_k, filters, results)

        logger.info(f"Pipeline V2 返回 {len(results)} 条结果")
        return results

    # ── 内部 ──────────────────────────────────────

    def _execute_strategy(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]],
        strategy: str,
    ) -> List[RetrievalResult]:
        """根据策略选择 Retriever。"""
        if strategy == "hybrid":
            return self._hybrid.retrieve(query, top_k, filters)
        elif strategy == "bm25":
            return self._bm25.retrieve(query, top_k, filters)
        else:
            # 默认 vector
            return self._vector.retrieve(query, top_k, filters)

    def _get_reranker(self):
        """安全获取 Reranker，无注册时返回 None。"""
        from core.registry import ServiceRegistry
        try:
            return ServiceRegistry().get(_RERANK_KEY)
        except Exception:
            return None


# ── 兼容旧接口 ──────────────────────────────────

# 保持 get_pipeline() 接口不变，内部升级为 V2
def get_pipeline() -> RetrievalPipelineV2:
    """获取 Retrieval Pipeline V2 实例（兼容 V1 调用方）。"""
    return RetrievalPipelineV2()
