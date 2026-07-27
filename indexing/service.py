"""IndexingService — 索引服务入口。

对外提供 index() 接口，内部委托 IndexPipeline 执行。
不直接创建 Embedding / VectorStore 实例，全部通过 Registry 获取。
"""

from core.logger import get_logger
from core.registry import get_service, register_service_factory

from indexing.exception import IndexingError
from indexing.model import IndexResult
from indexing.pipeline import IndexPipeline

logger = get_logger(__name__)


class IndexingService:
    """索引服务 — 提供统一索引入口。

    Usage::

        svc = IndexingService()
        result = svc.index(processed_document)
    """

    def __init__(self, pipeline: IndexPipeline | None = None):
        self._pipeline = pipeline or IndexPipeline()

    def index(self, document) -> IndexResult:
        """对 ProcessedDocument 执行索引。

        Args:
            document: processor.model.ProcessedDocument 实例。

        Returns:
            IndexResult（success / chunk_count / error）。

        Raises:
            IndexingError: 索引流程执行失败。
        """
        logger.info(f"开始索引: doc={document.document.id}")
        result = self._pipeline.execute(document)

        if not result.success:
            raise IndexingError(
                f"索引失败: doc={result.document_id}, error={result.error}"
            )

        return result


# ── Registry 注册 ──────────────────────────────

def _create_indexing_service() -> IndexingService:
    return IndexingService()


register_service_factory("indexing", _create_indexing_service)


def get_indexing_service() -> IndexingService:
    """获取 IndexingService 实例。"""
    return get_service("indexing", IndexingService)
