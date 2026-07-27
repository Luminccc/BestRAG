"""MetadataFilter — 基于文档 metadata 的结果过滤。

消费 Indexing 写入 VectorStore 的 metadata 字段。
只做过滤，不关心 metadata 从何而来。
"""

from typing import Any, Dict, List

from retrieval.retriever.model import RetrievalResult


class MetadataFilter:
    """元数据过滤器 — 按条件筛选举结果。"""

    def filter(self, results: List[RetrievalResult], conditions: Dict[str, Any]) -> List[RetrievalResult]:
        """过滤检索结果，保留 metadata 中满足所有条件的结果。

        Args:
            results:    待过滤的检索结果列表。
            conditions: 过滤条件（AND 关系），如 {"department": "finance", "year": "2025"}。

        Returns:
            过滤后的结果列表。若 conditions 为空则原样返回。
        """
        if not conditions:
            return results

        filtered: List[RetrievalResult] = []
        for r in results:
            if self._match(r.metadata, conditions):
                filtered.append(r)
        return filtered

    def _match(self, metadata: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        """检查 metadata 是否满足所有条件。值比较转字符串，兼容 Milvus JSON 转 string。"""
        for key, expected in conditions.items():
            actual = metadata.get(key)
            if actual is None:
                return False
            # 兼容不同类型（Milvus JSON 可能把 int → str）
            if str(actual) != str(expected):
                return False
        return True
