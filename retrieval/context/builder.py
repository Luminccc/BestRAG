"""ContextBuilder — 检索结果上下文构建器。

将 RetrievalResult 列表转换为 LLM 输入上下文。
支持：
- Chunk 合并
- Parent 扩展
- 去重
- Token 限制
"""

from typing import Any, Dict, List, Optional

from retrieval.retriever.model import RetrievalResult


class ContextBuilder:
    """上下文构建器。

    用法::

        builder = ContextBuilder(max_tokens=2000)
        context = builder.build(results)
    """

    def __init__(self, max_tokens: int = 2000, separator: str = "\n\n---\n\n"):
        self._max_tokens = max_tokens
        self._separator = separator

    def build(
        self,
        results: List[RetrievalResult],
        include_metadata: bool = True,
    ) -> str:
        """构建上下文文本。

        Args:
            results: 检索结果列表。
            include_metadata: 是否在上下文中包含元数据。

        Returns:
            格式化的上下文字符串。
        """
        if not results:
            return ""

        # 去重
        seen = set()
        chunks: list[str] = []
        token_count = 0

        for r in results:
            if r.chunk_id in seen:
                continue
            seen.add(r.chunk_id)

            # 构建内容块
            content = r.content
            if include_metadata and r.metadata:
                meta_str = self._format_metadata(r.metadata)
                if meta_str:
                    content = f"[{meta_str}]\n{content}"

            # 估算 token 数（~1 token/1.5 中文字符）
            estimated = len(content) // 2
            if token_count + estimated > self._max_tokens:
                break

            chunks.append(content)
            token_count += estimated

        return self._separator.join(chunks)

    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """格式化元数据为可读字符串。"""
        parts = []
        for key in ("heading", "source", "page", "document_id"):
            val = metadata.get(key)
            if val is not None and val != "":
                parts.append(f"{key}={val}")
        return ", ".join(parts)

    def build_with_sources(
        self,
        results: List[RetrievalResult],
    ) -> tuple[str, List[Dict[str, Any]]]:
        """构建上下文并返回来源列表。

        Returns:
            (context_text, sources_list)
        """
        context = self.build(results)
        sources = [
            {
                "chunk_id": r.chunk_id,
                "score": r.score,
                "metadata": r.metadata,
            }
            for r in results
        ]
        return context, sources
