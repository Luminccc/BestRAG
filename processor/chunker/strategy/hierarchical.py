"""HierarchicalChunkStrategy — 层级文档切分策略。

生成父子结构的 Chunk：
- Parent Chunk：整个章节的内容（全文）
- Child Chunk：章节内的段落级切分

用于 Hierarchical Retrieval，先检索 Parent 定位章节，再检索 Child 获取细节。
"""

from typing import List, Tuple

from processor.chunker.model import Chunk
from processor.chunker.strategy.base import BaseChunkStrategy
from processor.chunker.strategy.heading import HeadingChunkStrategy

_DEFAULT_CHUNK_SIZE = 500
_DEFAULT_OVERLAP = 50


class HierarchicalChunkStrategy(BaseChunkStrategy):
    """层级文档切分。

    先按标题切分为 Parent Chunk，再对每个 Parent 内的内容进行
    段落级切分产生 Child Chunk。

    Usage::

        strategy = HierarchicalChunkStrategy()
        chunks = strategy.split(text, document_id="xxx")
    """

    name: str = "hierarchical"

    def __init__(self, chunk_size: int = _DEFAULT_CHUNK_SIZE, overlap: int = _DEFAULT_OVERLAP):
        self._chunk_size = chunk_size
        self._overlap = overlap
        self._heading_strategy = HeadingChunkStrategy(chunk_size, overlap)

    def split(self, text: str, document_id: str) -> list[Chunk]:
        if not text.strip():
            return []

        # Step 1: 先用 Heading 策略切出章节（Parent Chunk）
        parent_chunks = self._heading_strategy.split(text, document_id)
        if not parent_chunks:
            # 无标题结构，退化为段落级切分
            return self._split_by_paragraphs(text, document_id)

        # Step 2: 为每个 Parent Chunk 生成 Child Chunks
        all_chunks: list[Chunk] = []
        for parent in parent_chunks:
            # 记录 Parent 信息
            parent_meta = {
                **parent.metadata,
                "is_parent": True,
                "strategy": "hierarchical",
                "child_count": 0,
            }
            parent.metadata = parent_meta
            all_chunks.append(parent)

            # 对 Parent 内容做段落级切分
            children = self._split_by_paragraphs(parent.content, document_id)
            if children:
                child_start = len(all_chunks)
                for i, child in enumerate(children):
                    child.metadata = {
                        "strategy": "hierarchical",
                        "parent_heading": parent_meta.get("heading", ""),
                        "is_parent": False,
                        "parent_index": parent.index,
                    }
                    child.index = child_start + i
                    all_chunks.append(child)

                # 更新 Parent 的 child_count
                parent.metadata["child_count"] = len(children)

        return all_chunks

    def _split_by_paragraphs(self, text: str, document_id: str) -> list[Chunk]:
        """按段落切分文本。"""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            return []

        chunks: list[Chunk] = []
        current_text = ""
        current_length = 0

        for para in paragraphs:
            para_len = len(para)

            if current_length + para_len + 1 <= self._chunk_size:
                if current_text:
                    current_text += "\n\n"
                current_text += para
                current_length += para_len + (2 if current_text else 0)
            else:
                if current_text:
                    chunks.append(Chunk(
                        document_id=document_id,
                        content=current_text,
                        index=len(chunks),
                        metadata={"strategy": "paragraph", "chunk_size": self._chunk_size},
                    ))
                current_text = para
                current_length = para_len

        if current_text:
            chunks.append(Chunk(
                document_id=document_id,
                content=current_text,
                index=len(chunks),
                metadata={"strategy": "paragraph", "chunk_size": self._chunk_size},
            ))

        return chunks
