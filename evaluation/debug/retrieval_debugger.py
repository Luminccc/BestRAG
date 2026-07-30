"""RetrievalDebugger — 检索问题诊断器。

回答"为什么这个问题检索失败？"
分析 Query / Retriever / Fusion / Chunk 各环节。
"""

from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.models.trace import Trace, Span

logger = get_logger("evaluation.debug")


class RetrievalDebugger:
    """检索调试器。

    诊断检索失败原因，给出优化建议。
    """

    def analyze(
        self,
        result_count: int,
        expected_count: int = 0,
        trace: Optional[Trace] = None,
        spans: Optional[List[Span]] = None,
    ) -> Dict[str, Any]:
        """诊断一次检索。

        Args:
            result_count: 实际返回结果数。
            expected_count: 期望结果数（0 表示未知）。
            trace: 关联的 Trace（可选）。
            spans: Trace 的 Span 列表（可选）。

        Returns:
            诊断结果，含问题分类和建议。
        """
        issues = []
        suggestions = []

        # 1. 检查结果数量
        if result_count == 0:
            issues.append("no_results")
            suggestions.append("检查向量库是否有数据")
            suggestions.append("检查 query 是否为空或过长")
        elif expected_count > 0 and result_count < expected_count:
            issues.append("insufficient_results")
            suggestions.append("降低 top_k 阈值或检查重排序策略")

        # 2. 检查 Trace 信息
        if trace and spans:
            # 检查 retriever spans
            retriever_spans = [s for s in spans if s.name.startswith("retriever_")]
            if not retriever_spans:
                issues.append("no_retriever_executed")
                suggestions.append("检查检索器是否已注册")

            # 检查错误
            for s in spans:
                if "error" in s.attributes:
                    issues.append(f"{s.name}_error")
                    suggestions.append(f"{s.name} 出现异常: {s.attributes['error']}")

        # 3. 通用建议
        if not suggestions:
            suggestions.append("检索正常，无需调整")

        return {
            "issues": issues,
            "suggestion": suggestions[0] if suggestions else "无建议",
            "all_suggestions": suggestions,
            "result_count": result_count,
        }

    def analyze_query(
        self,
        query: str,
        rewritten_query: str = "",
    ) -> Dict[str, Any]:
        """分析 Query 质量。

        Args:
            query: 原始查询。
            rewritten_query: 重写后的查询。

        Returns:
            查询分析结果。
        """
        issues = []
        suggestions = []

        if not query.strip():
            issues.append("empty_query")
            suggestions.append("查询内容不能为空")
        elif len(query) < 3:
            issues.append("query_too_short")
            suggestions.append("查询过短，建议扩写")
        elif len(query) > 200:
            issues.append("query_too_long")
            suggestions.append("查询过长，建议精简")

        if not rewritten_query:
            suggestions.append("考虑启用 Query Rewrite")
        elif rewritten_query != query:
            suggestions.append("Query Rewrite 已生效，检查改写质量")

        return {
            "query": query,
            "rewritten_query": rewritten_query,
            "issues": issues,
            "suggestion": suggestions[0] if suggestions else "查询正常",
            "all_suggestions": suggestions,
        }

    def analyze_chunk(
        self,
        chunk_count: int,
        chunk_strategy: str = "",
    ) -> Dict[str, Any]:
        """分析 Chunk 策略。

        Args:
            chunk_count: 切分的 Chunk 数量。
            chunk_strategy: 切分策略名称。

        Returns:
            Chunk 分析结果。
        """
        issues = []
        suggestions = []

        if chunk_count == 0:
            issues.append("no_chunks")
            suggestions.append("文档切分为空，检查文档内容")
        elif chunk_count == 1:
            issues.append("single_chunk")
            suggestions.append("只有一个 Chunk，考虑减小 chunk_size")

        if chunk_strategy:
            suggestions.append(f"当前 Chunk 策略: {chunk_strategy}")

        return {
            "chunk_count": chunk_count,
            "chunk_strategy": chunk_strategy,
            "issues": issues,
            "suggestion": suggestions[0] if suggestions else "Chunk 正常",
        }
