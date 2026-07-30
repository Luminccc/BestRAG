"""RecursiveChunkStrategy — 递归结构切分策略。

优先级：
    Paragraph split (\\n\\n) → Sentence split (. ! ?) → Character split

每层都遵守 chunk_size 限制，相邻 Chunk 之间保留 overlap 字符。
适合有自然段落和句子结构的文档（Markdown、TXT 等）。
"""

from processor.chunker.model import Chunk
from processor.chunker.strategy.base import BaseChunkStrategy

_DEFAULT_CHUNK_SIZE = 500
_DEFAULT_OVERLAP = 50

# 句子边界匹配：句号/问号/感叹号后跟空格或字符串结尾
_SENTENCE_BOUNDARY = ".!?"


class RecursiveChunkStrategy(BaseChunkStrategy):
    """递归结构切分。

    Usage::

        strategy = RecursiveChunkStrategy(chunk_size=500, overlap=50)
        chunks = strategy.split(text, document_id="xxx")
    """

    name: str = "recursive"

    def __init__(self, chunk_size: int = _DEFAULT_CHUNK_SIZE, overlap: int = _DEFAULT_OVERLAP):
        if chunk_size <= 0:
            raise ValueError(f"chunk_size 必须 > 0，当前值: {chunk_size}")
        if overlap < 0:
            raise ValueError(f"overlap 必须 >= 0，当前值: {overlap}")
        if overlap >= chunk_size:
            raise ValueError(f"overlap ({overlap}) 不能 >= chunk_size ({chunk_size})")

        self._chunk_size = chunk_size
        self._overlap = overlap

    def split(self, text: str, document_id: str) -> list[Chunk]:
        if not text:
            return []

        # 第 1 层：按段落切分
        paragraphs = self._split_paragraphs(text)

        # 第 2 层：对超长的段落进行句子级切分
        segments = []
        for para in paragraphs:
            if len(para) <= self._chunk_size:
                segments.append(para)
            else:
                sentences = self._split_sentences(para)
                segments.extend(sentences)

        # 第 3 层：对仍超长的段进行字符级硬切
        result_segments = []
        for seg in segments:
            if len(seg) <= self._chunk_size:
                result_segments.append(seg)
            else:
                sub = self._split_characters(seg)
                result_segments.extend(sub)

        # 生成 Chunk（带 overlap）
        return self._build_chunks(result_segments, document_id)

    # ---------- 分隔符切分 ----------

    def _split_paragraphs(self, text: str) -> list[str]:
        """按连续换行切分为段落，过滤空白。"""
        parts = text.split("\n\n")
        return [p for p in parts if p.strip()]

    def _split_sentences(self, text: str) -> list[str]:
        """按句子边界切分，保留标点符号。"""
        parts: list[str] = []
        current = ""
        for ch in text:
            current += ch
            if ch in _SENTENCE_BOUNDARY:
                stripped = current.strip()
                if stripped:
                    parts.append(stripped)
                current = ""
        # 剩余部分
        stripped = current.strip()
        if stripped:
            parts.append(stripped)
        return parts

    def _split_characters(self, text: str) -> list[str]:
        """按 chunk_size 硬切分。"""
        result: list[str] = []
        for i in range(0, len(text), self._chunk_size):
            result.append(text[i:i + self._chunk_size])
        return result

    # ---------- Chunk 组装 ----------

    def _build_chunks(self, segments: list[str], document_id: str) -> list[Chunk]:
        """将片段合并为不超过 chunk_size 的 Chunk，相邻 Chunk 间保留 overlap。"""
        if not segments:
            return []

        chunks: list[Chunk] = []
        merged_text = ""
        merged_length = 0
        text_offset = 0

        for seg in segments:
            seg_len = len(seg)

            if merged_length + seg_len + (1 if merged_text else 0) <= self._chunk_size:
                # 合并进当前 batch
                if merged_text:
                    merged_text += "\n"
                merged_text += seg
                merged_length = merged_length + seg_len + (1 if merged_text.count("\n") > 0 else 0)
            else:
                # 当前 batch 已满，产出 Chunk
                if merged_text.strip():
                    chunks.append(self._make_chunk(
                        merged_text, document_id, len(chunks), text_offset,
                    ))
                    text_offset += len(merged_text) - self._overlap

                # 新 batch，从上一个 Chunk 尾部截取 overlap 作为上下文
                if self._overlap > 0 and chunks:
                    prior = chunks[-1].content
                    if len(prior) > self._overlap:
                        prefix = prior[-self._overlap:] + "\n"
                    else:
                        prefix = prior + "\n"
                    merged_text = prefix + seg
                    merged_length = len(merged_text)
                else:
                    merged_text = seg
                    merged_length = seg_len

        # 最后一个 batch
        if merged_text.strip():
            chunks.append(self._make_chunk(
                merged_text, document_id, len(chunks), text_offset,
            ))

        return chunks

    def _make_chunk(self, text: str, document_id: str, index: int, offset: int) -> Chunk:
        return Chunk(
            document_id=document_id,
            content=text,
            index=index,
            metadata={
                "strategy": "recursive",
                "start": offset,
                "end": offset + len(text),
                "chunk_size": self._chunk_size,
                "overlap": self._overlap,
            },
        )
