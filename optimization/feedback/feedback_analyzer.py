"""FeedbackAnalyzer — 检索反馈分析器。

收集失败案例，分析原因，生成优化建议。
形成 Query → Retrieval → Trace → Evaluation → Analysis → Optimization 闭环。
"""

from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.models.retrieval import OptimizationSuggestion
from core.models.trace import Trace, TraceType, TraceStatus
from trace.storage import BaseTraceStorage, MemoryTraceStorage

logger = get_logger("optimization.feedback")


class FeedbackAnalyzer:
    """反馈分析器。

    分析检索失败案例，生成组件级别的优化建议。
    """

    def __init__(self, trace_storage: Optional[BaseTraceStorage] = None):
        self._trace_storage = trace_storage or MemoryTraceStorage()

    def collect_failures(self, limit: int = 50) -> List[Dict[str, Any]]:
        """收集失败的检索案例。"""
        traces = self._trace_storage.query(trace_type=TraceType.RETRIEVAL)[:limit]
        failures = []
        for t in traces:
            metrics = self._trace_storage.get_metrics(t.id)
            result_count = next((m.value for m in metrics if m.metric_name == "result_count"), 0)
            if result_count == 0:
                failures.append({
                    "trace_id": t.id,
                    "query": t.metadata.get("query", ""),
                    "result_count": int(result_count),
                })
        return failures

    def analyze_failure(self, trace: Trace) -> Optional[OptimizationSuggestion]:
        """分析单次失败，生成优化建议。"""
        if trace.status == TraceStatus.SUCCESS:
            return None

        spans = self._trace_storage.get_spans(trace.id)
        for s in spans:
            if "error" in s.attributes:
                return OptimizationSuggestion(
                    suggestion_type="retriever_change",
                    target=s.name,
                    reason=s.attributes["error"],
                    score_impact=-0.5,
                )

        metrics = self._trace_storage.get_metrics(trace.id)
        latency = next((m.value for m in metrics if m.metric_name == "latency_ms"), 0)
        if latency > 2000:
            return OptimizationSuggestion(
                suggestion_type="performance",
                target="retriever",
                reason=f"高延迟: {latency}ms",
                score_impact=-0.3,
            )

        return None

    def generate_suggestions(self, limit: int = 50) -> List[OptimizationSuggestion]:
        """批量分析失败案例，生成优化建议列表。"""
        traces = self._trace_storage.query(trace_type=TraceType.RETRIEVAL)[:limit]
        suggestions = []
        for t in traces:
            suggestion = self.analyze_failure(t)
            if suggestion:
                suggestions.append(suggestion)
        return suggestions
