"""IndexPipelineManager — 索引生命周期管理核心（v0.3 Phase 2 Trace 增强）。

支持 Trace 嵌入，记录每个索引步骤的耗时和属性。
"""

from time import time
from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.models.trace import TraceType, TraceStatus
from trace.context import TraceContext

logger = get_logger("knowledge.index_pipeline")


class IndexPipelineManager:
    """索引管线管理器（Trace 增强版）。

    每个 build/rebuild 操作自动创建 Trace，
    内部步骤（chunk/embed/write）各产生一个 Span。
    """

    def __init__(
        self,
        chunk_func: Optional[callable] = None,
        embed_func: Optional[callable] = None,
        write_func: Optional[callable] = None,
        trace_ctx: Optional[TraceContext] = None,
    ):
        self._chunk_func = chunk_func
        self._embed_func = embed_func
        self._write_func = write_func
        self._trace_ctx = trace_ctx

    # ── 构建策略 ──────────────────────────────────

    def build(self, doc) -> int:
        """全量索引构建（带 Trace）。"""
        doc_id = getattr(doc, "id", "unknown")
        logger.info(f"全量索引构建: doc={doc_id}")

        ctx = self._get_trace_ctx()
        trace = ctx.start_trace(TraceType.INDEX, metadata={"document_id": doc_id})

        try:
            with ctx.span("chunk", document_id=doc_id) as sp:
                chunks = self._do_chunk(doc)
                sp.attributes["chunk_count"] = len(chunks)

            if not chunks:
                ctx.record_event("chunk_empty", {"document_id": doc_id})
                ctx.end_trace(TraceStatus.SUCCESS)
                return 0

            with ctx.span("embed", chunk_count=len(chunks)) as sp:
                vectors = self._do_embed(chunks)
                sp.attributes["vector_count"] = len(vectors)

            with ctx.span("write", vector_count=len(vectors)) as sp:
                self._do_write(chunks, vectors)
                sp.attributes["written_count"] = len(chunks)

            ctx.record_metric("chunk_count", len(chunks))
            ctx.record_metric("vector_count", len(vectors))
            ctx.end_trace(TraceStatus.SUCCESS)

            return len(chunks)

        except Exception as e:
            ctx.record_event("build_failed", {"error": str(e)})
            ctx.end_trace(TraceStatus.FAILED)
            raise

    def rebuild(self, doc) -> int:
        """重建索引。"""
        logger.info(f"索引重建: doc={getattr(doc, 'id', 'unknown')}")
        return self.build(doc)

    def incremental(self, doc, changed_chunks: List) -> int:
        """增量更新索引（带 Trace）。"""
        doc_id = getattr(doc, "id", "unknown")
        logger.info(f"增量索引更新: doc={doc_id}, changed={len(changed_chunks)}")

        if not changed_chunks:
            return 0

        ctx = self._get_trace_ctx()
        ctx.start_trace(TraceType.INDEX, metadata={"document_id": doc_id, "mode": "incremental"})

        try:
            with ctx.span("incremental_embed", chunk_count=len(changed_chunks)):
                vectors = self._do_embed(changed_chunks)

            with ctx.span("incremental_write", vector_count=len(vectors)):
                self._do_write(changed_chunks, vectors)

            ctx.record_metric("changed_count", len(changed_chunks))
            ctx.end_trace(TraceStatus.SUCCESS)
            return len(changed_chunks)

        except Exception as e:
            ctx.record_event("incremental_failed", {"error": str(e)})
            ctx.end_trace(TraceStatus.FAILED)
            raise

    # ── 内部步骤 ──────────────────────────────────

    def _do_chunk(self, doc) -> List:
        if self._chunk_func:
            return self._chunk_func(doc)
        return [{"id": f"{getattr(doc, 'id', 'unknown')}_chunk_0", "content": doc.content}]

    def _do_embed(self, chunks: List) -> List:
        if self._embed_func:
            return self._embed_func(chunks)
        return []

    def _do_write(self, chunks: List, vectors: List) -> None:
        if self._write_func:
            self._write_func(chunks, vectors)

    def _get_trace_ctx(self) -> TraceContext:
        """获取 TraceContext（懒创建）。"""
        if self._trace_ctx is None:
            self._trace_ctx = TraceContext()
        return self._trace_ctx
