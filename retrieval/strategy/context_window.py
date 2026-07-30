"""ContextWindowRetrievalStrategy — 上下文窗口检索策略。

在基础检索后，为每个匹配的 Chunk 扩展上下文窗口，
返回相邻的 Chunk，解决 Chunk 过小导致上下文不足的问题。
"""

from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.strategy.retrieval import BaseRetrievalStrategy
from retrieval.retriever.model import RetrievalResult

logger = get_logger(__name__)


class ContextWindowRetrievalStrategy(BaseRetrievalStrategy):
    """上下文窗口检索 — 检索后扩展邻居 Chunk。"""

    name: str = "context_window"

    def __init__(self, window_size: int = 1):
        self._window_size = window_size
        from retrieval.strategy.vector import VectorRetrievalStrategy
        self._vector = VectorRetrievalStrategy()

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        # Step 1: 基础检索
        base_results = self._vector.retrieve(query, top_k, filters)

        if not base_results:
            return []

        # Step 2: 按 document_id 分组，扩展窗口
        doc_groups: Dict[str, list[RetrievalResult]] = {}
        for r in base_results:
            doc_id = r.metadata.get("document_id", "")
            if doc_id not in doc_groups:
                doc_groups[doc_id] = []
            doc_groups[doc_id].append(r)

        # Step 3: 对每组的每个结果，扩展其邻居（通过 index 排序）
        expanded: list[RetrievalResult] = []
        seen_ids = set()

        for doc_id, doc_results in doc_groups.items():
            # 按 index 排序
            doc_results.sort(key=lambda r: r.metadata.get("chunk_index", 0))

            for r in doc_results:
                chunk_index = r.metadata.get("chunk_index", 0)
                if chunk_index is None:
                    expanded.append(r)
                    continue

                # 添加前驱和后继邻居
                for offset in range(-self._window_size, self._window_size + 1):
                    if offset == 0:
                        continue
                    neighbor_idx = chunk_index + offset
                    if neighbor_idx < 0:
                        continue
                    # 创建邻居结果（score 降低）
                    neighbor = RetrievalResult(
                        chunk_id=f"{r.chunk_id}_ctx_{offset}",
                        score=r.score * 0.8 ** abs(offset),
                        content=r.content,
                        metadata={
                            **r.metadata,
                            "is_context_window": True,
                            "original_chunk_id": r.chunk_id,
                            "window_offset": offset,
                        },
                    )
                    expanded.append(neighbor)

                expanded.append(r)

        # 去重
        seen = set()
        deduped: list[RetrievalResult] = []
        for r in expanded:
            if r.chunk_id not in seen:
                seen.add(r.chunk_id)
                deduped.append(r)

        # 按 score 排序
        deduped.sort(key=lambda r: r.score, reverse=True)

        logger.info(
            f"ContextWindowRetrievalStrategy: {len(deduped)} 条结果 "
            f"(base={len(base_results)}, window={self._window_size})"
        )
        return deduped[:top_k * (1 + 2 * self._window_size)]
