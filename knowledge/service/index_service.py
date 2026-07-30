"""IndexService — 索引管理服务。

负责文档的索引构建、重建和增量更新。
通过 IndexPipelineManager 调用底层索引管线。
"""

from time import time
from typing import List, Optional

from core.logger import get_logger
from core.models.knowledge import Document, IndexRecord, IndexStatus
from core.repository.knowledge import IndexRepository
from core.service import BaseService

logger = get_logger("knowledge.index")


class IndexService(BaseService):
    """索引管理服务。

    管理文档索引生命周期，协调 IndexPipelineManager 执行实际索引。
    """

    name = "knowledge_index"

    def __init__(
        self,
        index_repo: Optional[IndexRepository] = None,
        pipeline_manager: Optional["IndexPipelineManager"] = None,  # noqa: F821
    ):
        self._index_repo = index_repo or IndexRepository()
        self._pipeline_manager = pipeline_manager

    def initialize(self) -> None:
        """初始化索引服务。"""
        logger.info("IndexService 初始化完成")

    def close(self) -> None:
        """释放资源。"""
        logger.info("IndexService 已关闭")

    # ── 索引管理 ─────────────────────────────────

    def build_index(
        self,
        doc: Document,
        embedding_model: str = "bge-m3",
        chunk_strategy: str = "",
        vector_store: str = "",
        content_hash: str = "",
    ) -> IndexRecord:
        """构建文档索引（全量构建，带增强字段）。

        Args:
            doc: 待索引的文档。
            embedding_model: 使用的 Embedding 模型。
            chunk_strategy: 切分策略名称。
            vector_store: 向量存储后端。
            content_hash: 文档内容哈希。

        Returns:
            索引记录。
        """
        import hashlib
        start = time()
        _hash = content_hash or hashlib.md5(doc.content.encode()).hexdigest()

        record = IndexRecord(
            document_id=doc.id,
            embedding_model=embedding_model,
            content_hash=_hash,
            chunk_strategy=chunk_strategy,
            vector_store=vector_store,
            status=IndexStatus.BUILDING,
        )
        self._index_repo.save(record)

        try:
            chunk_count = 0
            if self._pipeline_manager:
                chunk_count = self._pipeline_manager.build(doc)

            record.chunk_count = chunk_count
            record.index_time = round(time() - start, 3)
            record.build_duration = round(time() - start, 3)
            record.status = IndexStatus.READY
            self._index_repo.save(record)

            logger.info(
                f"索引构建完成: doc={doc.id}, chunks={chunk_count}, "
                f"耗时={record.index_time}s"
            )
            return record

        except Exception as e:
            record.status = IndexStatus.FAILED
            self._index_repo.save(record)
            logger.error(f"索引构建失败: doc={doc.id}, error={e}")
            return record

    def rebuild_index(self, doc: Document, embedding_model: str = "bge-m3") -> IndexRecord:
        """重建文档索引（删除旧索引后重新构建）。

        对于增量更新场景，先清理旧索引记录再构建新索引。
        """
        # 清理旧索引记录
        old_records = self._index_repo.list(document_id=doc.id)
        for r in old_records:
            self._index_repo.delete(r.id)

        logger.info(f"索引重建: doc={doc.id}, 清理 {len(old_records)} 条旧记录")
        return self.build_index(doc, embedding_model)

    def incremental_update(self, doc: Document, embedding_model: str = "bge-m3") -> IndexRecord:
        """增量更新索引。

        检查是否存在旧索引，存在则重建，不存在则全量构建。
        """
        old = self._index_repo.find_by_document(doc.id)
        if old is None:
            logger.info(f"无旧索引记录，执行全量构建: doc={doc.id}")
            return self.build_index(doc, embedding_model)

        logger.info(f"检测到旧索引，执行重建: doc={doc.id}, old_status={old.status}")
        return self.rebuild_index(doc, embedding_model)

    def get_index_status(self, document_id: str) -> Optional[IndexRecord]:
        """查询文档的索引状态。"""
        return self._index_repo.find_by_document(document_id)
