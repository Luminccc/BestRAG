"""KnowledgeAnalyzer — 知识库质量分析。

基于 IndexRecord / Trace / Evaluation 分析知识库质量。
检测死亡文档、低质量 Chunk 和缺失知识。
"""

from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.models.knowledge import IndexRecord, IndexStatus
from core.models.trace import Trace, TraceType
from trace.storage import BaseTraceStorage, MemoryTraceStorage

logger = get_logger("knowledge.intelligence")


class KnowledgeAnalyzer:
    """知识库分析器。

    分析知识库健康度，检测问题并给出建议。
    """

    def __init__(self, trace_storage: Optional[BaseTraceStorage] = None):
        self._trace_storage = trace_storage or MemoryTraceStorage()

    def analyze_documents(
        self,
        index_records: List[IndexRecord],
        doc_ids: List[str],
    ) -> List[Dict[str, Any]]:
        """分析文档健康度。

        检测：
        - 死亡文档（从未被召回）
        - 索引失败的文档

        Args:
            index_records: 索引记录列表。
            doc_ids: 所有文档 ID 列表。

        Returns:
            每个文档的分析结果。
        """
        # 获取所有检索 Trace 中命中的文档
        traces = self._trace_storage.query(trace_type=TraceType.RETRIEVAL)
        retrieved_docs: set = set()
        for t in traces:
            metrics = self._trace_storage.get_metrics(t.id)
            for m in metrics:
                if m.metric_name == "result_count" and m.value > 0:
                    retrieved_docs.add(t.metadata.get("document_id", ""))

        indexed = {r.document_id for r in index_records if r.status == IndexStatus.READY}
        failed = {r.document_id for r in index_records if r.status == IndexStatus.FAILED}

        results = []
        for doc_id in doc_ids:
            issues = []
            if doc_id in failed:
                issues.append("index_failed")
            if doc_id in indexed and doc_id not in retrieved_docs:
                issues.append("dead_document")

            results.append({
                "document_id": doc_id,
                "indexed": doc_id in indexed,
                "retrieved": doc_id in retrieved_docs,
                "issues": issues,
                "recommendation": self._recommend(issues),
            })
        return results

    def analyze_trace_quality(self, trace_id: str) -> Dict[str, Any]:
        """分析一条检索 Trace 的质量。"""
        trace = self._trace_storage.get(trace_id)
        if trace is None:
            return {"error": "trace_not_found"}

        spans = self._trace_storage.get_spans(trace_id)
        metrics = self._trace_storage.get_metrics(trace_id)

        result_count = next((m.value for m in metrics if m.metric_name == "result_count"), 0)
        latency = next((m.value for m in metrics if m.metric_name == "latency_ms"), 0)

        issues = []
        if result_count == 0:
            issues.append("no_results")
        if latency > 1000:
            issues.append("high_latency")

        return {
            "trace_id": trace_id,
            "result_count": int(result_count),
            "latency_ms": latency,
            "issues": issues,
            "healthy": len(issues) == 0,
        }

    def detect_missing_knowledge(
        self,
        failed_queries: List[str],
        retrieval_results: Dict[str, int],
    ) -> List[Dict[str, Any]]:
        """检测缺失知识。

        区分"检索失败"和"知识不存在"。

        Args:
            failed_queries: 检索结果为 0 的查询列表。
            retrieval_results: 查询 → 结果数 映射。
        """
        findings = []
        for query in failed_queries:
            count = retrieval_results.get(query, 0)
            if count == 0:
                findings.append({
                    "query": query,
                    "type": "knowledge_missing" if len(query) > 10 else "retrieval_failure",
                    "suggestion": "需要补充相关知识" if len(query) > 10 else "检查检索策略",
                })
        return findings

    @staticmethod
    def _recommend(issues: List[str]) -> str:
        if "index_failed" in issues:
            return "重新执行索引"
        if "dead_document" in issues:
            return "检查文档相关性，考虑重新索引"
        return "正常"
