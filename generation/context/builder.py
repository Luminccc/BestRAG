"""ContextBuilder — 将 RetrievalResult 列表整理为 LLM 上下文。

处理：编号、去重、长度限制、metadata 保留。
"""

from typing import List

from retrieval.retriever.model import RetrievalResult


class ContextBuilder:
    """检索结果 → 结构化上下文字符串。"""

    def __init__(self, max_length: int = 8000):
        self._max_length = max_length

    def build(self, results: List[RetrievalResult]) -> str:
        """将检索结果格式化为编号文档块。

        Args:
            results: Retrieval 返回的结果列表。

        Returns:
            格式如：
            [Document 1]
            xxx content

            [Document 2]
            xxx content
        """
        if not results:
            return ""

        # 去重（按 chunk_id）
        seen: set[str] = set()
        unique: List[RetrievalResult] = []
        for r in results:
            if r.chunk_id not in seen:
                seen.add(r.chunk_id)
                unique.append(r)

        blocks: List[str] = []
        total_len = 0
        for i, r in enumerate(unique):
            block = f"[Document {i + 1}]\n{r.content}"
            if total_len + len(block) > self._max_length:
                break
            blocks.append(block)
            total_len += len(block)

        return "\n\n".join(blocks)
