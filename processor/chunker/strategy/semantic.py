"""SemanticChunkStrategy — 基于语义相似度的文档切分策略。

流程：
1. 将文本切分为句子
2. 通过 SimilarityProvider 计算相邻句子相似度
3. 在相似度明显下降处检测切分边界
4. 合并句子为 Chunk

适合：长文报告、论文、需要语义完整性的文档。

v0.2.5 升级：
- 使用 SimilarityProvider 替代硬编码 Jaccard
- 支持配置选择相似度算法
"""

from typing import Optional

from core.provider import BaseSimilarityProvider, JaccardSimilarityProvider
from processor.chunker.model import Chunk
from processor.chunker.strategy.base import BaseChunkStrategy

_DEFAULT_CHUNK_SIZE = 500
_DEFAULT_OVERLAP = 50
_DEFAULT_SIMILARITY_THRESHOLD = 0.6

# 句子边界字符
_SENTENCE_BOUNDARY = ".!?\n"


class SemanticChunkStrategy(BaseChunkStrategy):
    """基于语义相似度的文档切分。

    Usage::

        strategy = SemanticChunkStrategy()
        chunks = strategy.split(text, document_id="xxx")
    """

    name: str = "semantic"

    def __init__(
        self,
        chunk_size: int = _DEFAULT_CHUNK_SIZE,
        overlap: int = _DEFAULT_OVERLAP,
        similarity_threshold: float = _DEFAULT_SIMILARITY_THRESHOLD,
        similarity_provider: Optional[BaseSimilarityProvider] = None,
    ):
        self._chunk_size = chunk_size
        self._overlap = overlap
        self._threshold = similarity_threshold
        self._provider = similarity_provider or JaccardSimilarityProvider()

    def split(self, text: str, document_id: str) -> list[Chunk]:
        if not text.strip():
            return []

        sentences = self._split_sentences(text)
        if not sentences:
            return []

        similarities = self._compute_similarities(sentences)
        chunks = self._merge_sentences(sentences, similarities, document_id)
        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """按句子边界切分文本。"""
        sentences: list[str] = []
        current = ""

        for ch in text:
            current += ch
            if ch in _SENTENCE_BOUNDARY:
                stripped = current.strip()
                if stripped:
                    sentences.append(stripped)
                current = ""

        stripped = current.strip()
        if stripped:
            sentences.append(stripped)

        return sentences

    def _compute_similarities(self, sentences: list[str]) -> list[float]:
        """通过 SimilarityProvider 计算相邻句子相似度。"""
        similarities: list[float] = []
        for i in range(len(sentences) - 1):
            sim = self._provider.similarity(sentences[i], sentences[i + 1])
            similarities.append(sim)
        return similarities

    def _merge_sentences(
        self,
        sentences: list[str],
        similarities: list[float],
        document_id: str,
    ) -> list[Chunk]:
        """根据相似度将句子合并为 Chunk。"""
        if not sentences:
            return []

        chunks: list[Chunk] = []
        current_sentences: list[str] = [sentences[0]]
        current_length = len(sentences[0])

        for i in range(1, len(sentences)):
            sim = similarities[i - 1] if i - 1 < len(similarities) else 1.0
            sentence = sentences[i]
            sentence_len = len(sentence)

            should_split = (
                sim < self._threshold
                or current_length + sentence_len + 1 > self._chunk_size
            )

            if should_split and current_sentences:
                chunk_text = " ".join(current_sentences)
                chunks.append(Chunk(
                    document_id=document_id,
                    content=chunk_text,
                    index=len(chunks),
                    metadata={
                        "strategy": "semantic",
                        "sentences": len(current_sentences),
                        "threshold": self._threshold,
                    },
                ))
                overlap_text = self._get_overlap(current_sentences)
                current_sentences = [overlap_text, sentence] if overlap_text else [sentence]
                current_length = len(" ".join(current_sentences))
            else:
                current_sentences.append(sentence)
                current_length += sentence_len + 1

        if current_sentences:
            chunk_text = " ".join(current_sentences)
            chunks.append(Chunk(
                document_id=document_id,
                content=chunk_text,
                index=len(chunks),
                metadata={
                    "strategy": "semantic",
                    "sentences": len(current_sentences),
                    "threshold": self._threshold,
                },
            ))

        return chunks

    def _get_overlap(self, sentences: list[str]) -> str:
        """从句子列表末尾获取 overlap 文本。"""
        if not sentences or self._overlap <= 0:
            return ""
        result = ""
        for s in reversed(sentences):
            candidate = s + " " + result if result else s
            if len(candidate) > self._overlap:
                break
            result = candidate
        return result.strip()
