"""Indexing Stages — 索引流程的阶段抽象。

将 IndexPipeline 拆分为独立阶段，便于扩展和测试。
"""

from abc import ABC, abstractmethod
from typing import Any, List

from indexing.model import IndexChunk


class BaseIndexStage(ABC):
    """索引阶段基类。"""

    name: str = "base_stage"

    @abstractmethod
    def process(self, chunks: List[IndexChunk], **kwargs: Any) -> List[IndexChunk]:
        """处理索引块列表。

        Args:
            chunks: 输入索引块列表。
            **kwargs: 扩展参数。

        Returns:
            处理后的索引块列表。
        """


class MetadataEnrichmentStage(BaseIndexStage):
    """元数据增强阶段：补充索引需要的检索字段。"""

    name: str = "metadata_enrich"

    def process(self, chunks: list[IndexChunk], **kwargs: Any) -> list[IndexChunk]:
        for chunk in chunks:
            chunk.metadata.setdefault("index_version", kwargs.get("version", "v1"))
        return chunks


class EmbeddingStage(BaseIndexStage):
    """Embedding 阶段：批量生成向量。"""

    name: str = "embedding"

    def __init__(self, batch_size: int = 32):
        self._batch_size = batch_size

    def process(self, chunks: list[IndexChunk], **kwargs: Any) -> list[IndexChunk]:
        from core.config import get_config
        from core.registry import get_service

        texts = [c.content for c in chunks]
        if not texts:
            return chunks

        provider = get_service("embedding")
        cfg = get_config().indexing
        bs = cfg.batch_size or self._batch_size

        all_vectors: list[list[float]] = []
        for i in range(0, len(texts), bs):
            batch = texts[i:i + bs]
            raw = provider.embed_documents(batch)
            if raw and hasattr(raw[0], "vector"):
                all_vectors.extend(r.vector for r in raw)
            else:
                all_vectors.extend(raw)

        for chunk, vec in zip(chunks, all_vectors):
            chunk.embedding = vec

        return chunks


class WriterStage(BaseIndexStage):
    """写入阶段：将索引块写入 VectorStore。"""

    name: str = "writer"

    def process(self, chunks: list[IndexChunk], **kwargs: Any) -> list[IndexChunk]:
        from core.registry import get_service

        ready = [c for c in chunks if c.embedding is not None]
        if not ready:
            return chunks

        vectors = [c.embedding for c in ready]  # type: ignore
        texts = [c.content for c in ready]
        metadatas = [c.metadata for c in ready]
        ids = [c.id for c in ready]

        store = get_service("vector_store")
        store.add(vectors, texts, metadatas, ids)

        return chunks
