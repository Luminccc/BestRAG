"""RetrievalTraceAnalyzer — 基于 Trace 的检索分析。

利用 Phase 2 Trace 数据，分析检索管线的每个环节。
输出各环节的耗时、贡献度和失败原因。
"""

from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.models.trace import Trace, TraceType, Metric
from trace.storage import BaseTraceStorage, MemoryTraceStorage

logger = get_logger("evaluation.analyzer")


class RetrievalTraceAnalyzer:
    """检索 Trace 分析器。

    分析检索管线的每个步骤，输出结构化分析报告。
    """

    def __init__(self, storage: Optional[BaseTraceStorage] = None):
        self._storage = storage or MemoryTraceStorage()

    def analyze(self, trace: Trace) -> Dict[str, Any]:
        """分析一条检索 Trace。

        Args:
            trace: 检索 Trace。

        Returns:
            分析结果，包含各环节耗时、检索贡献和失败原因。
        """
        spans = self._storage.get_spans(trace.id)
        metrics = self._storage.get_metrics(trace.id)

        # 提取各环节耗时
        latency_info = self._extract_latency(spans)

        # 提取检索器贡献度
        retriever_contrib = self._retriever_contribution(spans)

        # 提取融合效果
        fusion_effect = self._fusion_effect(spans)

        # 提取失败原因
        failure = self._failure_reason(spans, trace)

        # 获取 top 文档
        top_documents = self._top_documents(metrics)

        return {
            "trace_id": trace.id,
            "latency": latency_info,
            "retriever_contribution": retriever_contrib,
            "fusion_effect": fusion_effect,
            "top_documents": top_documents,
            "failure_reason": failure,
        }

    def analyze_multiple(self, traces: List[Trace]) -> List[Dict[str, Any]]:
        """批量分析多条 Trace。"""
        return [self.analyze(t) for t in traces]

    # ── 内部分析方法 ──────────────────────────────

    def _extract_latency(self, spans) -> Dict[str, float]:
        latency = {}
        for s in spans:
            latency[s.name] = round(s.duration_ms, 2)
        return latency

    def _retriever_contribution(self, spans) -> Dict[str, int]:
        contrib = {}
        for s in spans:
            if s.name.startswith("retriever_"):
                name = s.name.replace("retriever_", "")
                contrib[name] = s.attributes.get("result_count", 0)
        return contrib

    def _fusion_effect(self, spans) -> Dict[str, Any]:
        for s in spans:
            if s.name == "fusion":
                return {
                    "method": s.attributes.get("method", ""),
                    "input_count": s.attributes.get("input_count", 0),
                    "output_count": s.attributes.get("output_count", 0),
                }
        return {}

    def _failure_reason(self, spans, trace: Trace) -> str:
        if trace.status.name == "SUCCESS":
            return ""

        for s in spans:
            if "error" in s.attributes:
                return f"{s.name}: {s.attributes['error']}"
        return trace.status.name

    def _top_documents(self, metrics) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in metrics if not m.metric_name.startswith("latency")]
