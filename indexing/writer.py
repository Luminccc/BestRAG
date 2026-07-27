"""VectorWriter — 将 IndexChunk 写入 VectorStore。

依赖 Registry 获取 vectorstore Provider，不关心底层是 Milvus 还是其他。
"""

from core.logger import get_logger
from core.registry import get_service
from indexing.model import IndexChunk

logger = get_logger(__name__)

# Registry key（与 retrieval/vectorstore/service.py 注册名一致）
_VECTORSTORE_KEY = "vector_store"


class VectorWriter:
    """向量写入器 — 批量写 IndexChunk 到 VectorStore。"""

    def write(self, chunks: list[IndexChunk]) -> list[str]:
        """将 IndexChunk 列表写入 VectorStore。

        Args:
            chunks: 已填充 embedding 的索引块列表。

        Returns:
            成功写入的 ID 列表。
        """
        if not chunks:
            return []

        # 只有嵌入完成的 chunk 才写入
        ready = [c for c in chunks if c.embedding is not None]
        if not ready:
            logger.warning("没有可写入的 chunk（全部缺少 embedding）")
            return []

        vectors = [c.embedding for c in ready]  # type: ignore
        texts = [c.content for c in ready]
        metadatas = [c.metadata for c in ready]
        ids = [c.id for c in ready]

        store = get_service(_VECTORSTORE_KEY)
        result_ids = store.add(vectors, texts, metadatas, ids)

        logger.info(f"VectorWriter 写入 {len(result_ids)} 条向量")
        return result_ids
