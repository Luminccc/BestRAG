"""TraceService — 可视化数据 API。

提供前端 Dashboard 所需的数据查询接口：
- Traces 查询与详情
- 延迟指标
- 检索分析
- 索引构建追踪
"""

from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.models.trace import Trace, TraceType, Metric
from trace.storage import BaseTraceStorage, MemoryTraceStorage

logger = get_logger("trace.service")


class TraceService:
    """Trace 服务。

    提供 Visualization 层所需的数据查询能力。
    """

    def __init__(self, storage: Optional[BaseTraceStorage] = None):
        self._storage = storage or MemoryTraceStorage()

    # ── Trace 查询 ─────────────────────────────────

    def query_traces(
        self,
        trace_type: Optional[TraceType] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """查询 Trace 列表（Dashboard 概览）。"""
        filters = {}
        if trace_type:
            filters["trace_type"] = trace_type
        traces = self._storage.query(**filters)[:limit]
        return [self._trace_to_view(t) for t in traces]

    def get_trace_detail(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """获取 Trace 详细信息（含 Spans/Metrics）。"""
        trace = self._storage.get(trace_id)
        if trace is None:
            return None

        spans = self._storage.get_spans(trace_id)
        metrics = self._storage.get_metrics(trace_id)

        return {
            **self._trace_to_view(trace),
            "spans": [s.to_dict() for s in spans],
            "metrics": [m.to_dict() for m in metrics],
        }

    # ── 指标聚合 ──────────────────────────────────

    def get_latency_metrics(
        self,
        trace_type: Optional[TraceType] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """获取延迟指标列表。"""
        filters = {}
        if trace_type:
            filters["trace_type"] = trace_type
        traces = self._storage.query(**filters)[:limit]

        results = []
        for t in traces:
            metrics = self._storage.get_metrics(t.id)
            latency = next((m for m in metrics if m.metric_name == "latency_ms"), None)
            results.append({
                "trace_id": t.id,
                "trace_type": t.trace_type.value if hasattr(t.trace_type, "value") else t.trace_type,
                "latency_ms": latency.value if latency else 0,
                "created_at": t.created_at.isoformat() if t.created_at else "",
            })
        return results

    def get_index_traces(self, document_id: str) -> List[Dict[str, Any]]:
        """获取文档的索引构建 Trace。"""
        traces = self._storage.query(trace_type=TraceType.INDEX)
        return [
            self._trace_to_view(t) for t in traces
            if t.metadata.get("document_id") == document_id
        ]

    def get_retrieval_analysis(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取检索分析数据。"""
        traces = self._storage.query(trace_type=TraceType.RETRIEVAL)[:limit]
        results = []
        for t in traces:
            metrics = self._storage.get_metrics(t.id)
            latency = next((m for m in metrics if m.metric_name == "latency_ms"), None)
            result_count = next((m for m in metrics if m.metric_name == "result_count"), None)
            results.append({
                "trace_id": t.id,
                "query": t.metadata.get("query", ""),
                "latency_ms": latency.value if latency else 0,
                "result_count": int(result_count.value) if result_count else 0,
                "created_at": t.created_at.isoformat() if t.created_at else "",
            })
        return results

    # ── 统计概览 ──────────────────────────────────

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """获取 Dashboard 概览统计。"""
        all_traces = self._storage.query()
        retrieval_traces = self._storage.query(trace_type=TraceType.RETRIEVAL)
        index_traces = self._storage.query(trace_type=TraceType.INDEX)

        total_latency = 0.0
        for t in retrieval_traces:
            metrics = self._storage.get_metrics(t.id)
            lat = next((m for m in metrics if m.metric_name == "latency_ms"), None)
            if lat:
                total_latency += lat.value

        return {
            "total_traces": len(all_traces),
            "retrieval_count": len(retrieval_traces),
            "index_count": len(index_traces),
            "avg_retrieval_latency_ms": round(total_latency / len(retrieval_traces), 2) if retrieval_traces else 0,
        }

    # ── 内部转换 ──────────────────────────────────

    def _trace_to_view(self, trace: Trace) -> Dict[str, Any]:
        return {
            "trace_id": trace.id,
            "trace_type": trace.trace_type.value if hasattr(trace.trace_type, "value") else trace.trace_type,
            "status": trace.status.value if hasattr(trace.status, "value") else trace.status,
            "span_count": trace.span_count,
            "created_at": trace.created_at.isoformat() if trace.created_at else "",
            "metadata": trace.metadata,
        }
