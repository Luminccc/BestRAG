"""Retrieval Pipeline V3 — 策略驱动检索流程编排（Trace 增强版）。

完整链路::

    Query
      │
      ▼
    Trace Start
      │
      ▼
    Query Rewrite Span
      │
      ▼
    Retrieval Cache Check
      │ (miss)
      ▼
    Retriever Pipeline (multi-strategy)
      │
      ▼
    Fusion Span
      │
      ▼
    Reranker Span
      │
      ▼
    Context Builder Span
      │
      ▼
    Trace End → Storage
"""

from typing import Any, Dict, List, Optional

from core.config import get_config
from core.logger import get_logger
from core.models.trace import TraceStatus, TraceType
from core.strategy.fusion import RRFFusionStrategy, WeightedFusionStrategy
from core.strategy.query import SimpleQueryRewriteStrategy
from retrieval.context.builder import ContextBuilder
from retrieval.retriever.model import RetrievalResult
from retrieval.strategy import (
    BM25RetrievalStrategy,
    HybridRetrievalStrategy,
    VectorRetrievalStrategy,
)
from trace.context import TraceContext

logger = get_logger(__name__)


class RetrievalTrace:
    """检索轨迹记录 — 兼容旧接口，同时转为 Trace 模型。"""

    def __init__(self):
        self.query: str = ""
        self.rewritten_query: str = ""
        self.strategies: list[str] = []
        self.fusion: str = ""
        self.latency_ms: float = 0.0
        self.result_count: int = 0
        self.results: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "rewritten_query": self.rewritten_query,
            "strategies": self.strategies,
            "fusion": self.fusion,
            "latency_ms": self.latency_ms,
            "result_count": self.result_count,
        }


class RetrievalPipelineV3:
    """检索管线 V3 — 策略驱动、可组合、可追踪。

    Usage::

        pipeline = RetrievalPipelineV3()
        results, trace = pipeline.retrieve("如何部署?")
    """

    def __init__(
        self,
        retrievers: Optional[Dict[str, Any]] = None,
        fusion_strategy: Optional[Any] = None,
        rewrite_strategy: Optional[Any] = None,
        context_builder: Optional[ContextBuilder] = None,
        trace_ctx: Optional[TraceContext] = None,
    ):
        self._retrievers = retrievers or {
            "vector": VectorRetrievalStrategy(),
            "bm25": BM25RetrievalStrategy(),
            "hybrid": HybridRetrievalStrategy(),
        }
        self._fusion = fusion_strategy or RRFFusionStrategy()
        self._rewrite = rewrite_strategy or SimpleQueryRewriteStrategy()
        self._context = context_builder or ContextBuilder()
        self._trace_ctx = trace_ctx

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        retriever_names: Optional[List[str]] = None,
        enable_rewrite: bool = True,
        enable_fusion: bool = True,
        filters: Optional[Dict[str, Any]] = None,
    ) -> tuple[List[RetrievalResult], RetrievalTrace]:
        """执行检索管线（带 Trace）。

        Args:
            query: 用户查询。
            top_k: 返回结果数。
            retriever_names: 使用的检索器列表（默认 ["vector"]）。
            enable_rewrite: 是否启用查询重写。
            enable_fusion: 是否启用融合。
            filters: 元数据过滤条件。

        Returns:
            (results, trace)
        """
        import time
        trace = RetrievalTrace()
        trace.query = query
        start = time.time()

        # 开始 Trace
        ctx = self._get_trace_ctx()
        ctx.start_trace(TraceType.RETRIEVAL, metadata={"query": query, "top_k": top_k})

        # Step 1: Query Rewrite
        rewritten = query
        if enable_rewrite:
            with ctx.span("query_rewrite", original_query=query) as sp:
                try:
                    rewritten = self._rewrite.rewrite(query)
                    sp.attributes["rewritten"] = rewritten
                except Exception as e:
                    logger.warning(f"Query rewrite 失败: {e}")
                    sp.attributes["error"] = str(e)
        trace.rewritten_query = rewritten

        # Step 2: 多路检索
        retriever_names = retriever_names or ["vector"]
        all_results: List[List[RetrievalResult]] = []

        for name in retriever_names:
            retriever = self._retrievers.get(name)
            if retriever is None:
                logger.warning(f"检索器 '{name}' 未注册，跳过")
                continue

            with ctx.span(f"retriever_{name}", strategy=name, top_k=top_k) as sp:
                try:
                    results = retriever.retrieve(rewritten, top_k=top_k, filters=filters)
                    all_results.append(results)
                    trace.strategies.append(name)
                    sp.attributes["result_count"] = len(results)
                except Exception as e:
                    logger.error(f"检索器 '{name}' 失败: {e}")
                    sp.attributes["error"] = str(e)

        if not all_results:
            elapsed = (time.time() - start) * 1000
            trace.latency_ms = elapsed
            ctx.record_event("retrieval_empty", {"query": query})
            ctx.end_trace(TraceStatus.SUCCESS)
            return [], trace

        # Step 3: Fusion
        final_results = all_results[0]
        if enable_fusion and len(all_results) > 1:
            with ctx.span("fusion", method=self._fusion.name, input_count=len(all_results)) as sp:
                try:
                    fused = self._fusion.fuse(all_results)
                    trace.fusion = self._fusion.name
                    final_results = fused
                    sp.attributes["output_count"] = len(fused)
                except Exception as e:
                    logger.warning(f"Fusion 失败: {e}")
                    sp.attributes["error"] = str(e)

        # 截断
        final_results = final_results[:top_k]

        elapsed = (time.time() - start) * 1000
        trace.latency_ms = elapsed
        trace.result_count = len(final_results)

        ctx.record_metric("latency_ms", elapsed)
        ctx.record_metric("result_count", len(final_results))
        ctx.end_trace(TraceStatus.SUCCESS)

        logger.info(
            f"PipelineV3: query={query[:40]}... "
            f"strategies={trace.strategies} fusion={trace.fusion} "
            f"results={trace.result_count} latency={elapsed:.0f}ms"
        )
        return final_results, trace

    def build_context(
        self,
        results: List[RetrievalResult],
        max_tokens: int = 2000,
    ) -> str:
        """从检索结果构建 LLM 上下文。"""
        return self._context.build(results)

    def get_retriever_names(self) -> list[str]:
        """列出所有已注册检索器。"""
        return list(self._retrievers.keys())

    def _get_trace_ctx(self) -> TraceContext:
        if self._trace_ctx is None:
            self._trace_ctx = TraceContext()
        return self._trace_ctx


# 兼容入口
def get_pipeline_v3() -> RetrievalPipelineV3:
    return RetrievalPipelineV3()
