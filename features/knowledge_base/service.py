"""KnowledgeBaseService — 知识库生命周期管理。

提供知识库核心能力：
- ingest: 上传文档 → 处理 → 切分 → 索引
- status: 查看知识库状态

内部调用：
    IngressService → DocumentService → ProcessorService → IndexingService
"""

from pathlib import Path
from time import time

from core.logger import get_logger
from features.model import KnowledgeIngestRequest, KnowledgeIngestResponse, KnowledgeStatusResponse

logger = get_logger("features.knowledge_base")


class KnowledgeBaseService:
    """知识库管理服务。

    Usage::

        svc = KnowledgeBaseService(
            ingress_service=ingress_svc,
            document_service=doc_svc,
            processor_service=proc_svc,
            indexing_service=idx_svc,
        )
        result = svc.ingest(KnowledgeIngestRequest(file_path="/data/doc.pdf"))
        status = svc.status()
    """

    def __init__(
        self,
        ingress_service=None,     # IngressService
        document_service=None,    # DocumentService
        processor_service=None,   # ProcessorService
        indexing_service=None,    # IndexingService
    ):
        self._ingress = ingress_service
        self._doc = document_service
        self._processor = processor_service
        self._indexing = indexing_service
        # 轻量内存计数器（V1 简化实现）
        self._doc_count = 0
        self._chunk_count = 0

    # ── 公开接口 ──────────────────────────────────

    def ingest(self, request: KnowledgeIngestRequest) -> KnowledgeIngestResponse:
        """摄入文档：上传 → 处理 → 切分 → 索引。

        流程：
            1. IngressService → InputFile
            2. DocumentService → Document
            3. ProcessorService → ProcessedDocument (chunks)
            4. IndexingService → IndexResult

        Args:
            request: 包含文件路径和处理参数的请求。

        Returns:
            KnowledgeIngestResponse（含 document_id / chunk_count）。
        """
        start = time()
        file_path = request.file_path

        # 校验文件存在
        if not Path(file_path).exists():
            return KnowledgeIngestResponse(
                success=False,
                message=f"文件不存在: {file_path}",
            )

        try:
            # ── Step 1: Ingress → InputFile ──
            from ingress.model.source import LocalSource
            input_file = None
            if self._ingress:
                input_file = self._ingress.ingest(LocalSource(Path(file_path)))

            # ── Step 2: Document Parsing ──
            if self._doc is None:
                return KnowledgeIngestResponse(
                    success=False, message="DocumentService 未注入",
                )
            doc = self._doc.create_document(file_path)
            doc_id = doc.id or "unknown"
            logger.info(f"文档解析完成: {doc_id}, {len(doc.content)} chars")

            # ── Step 3: Processor → Clean + Chunk ──
            chunk_count = 0
            if self._processor:
                processed = self._processor.process(doc, request.strategy)
                chunk_count = len(processed.chunks) if processed.chunks else 0
                logger.info(f"文档处理完成: {chunk_count} chunks")

                # ── Step 4: Indexing ──
                if self._indexing:
                    index_result = self._indexing.index(processed)
                    if not index_result.success:
                        return KnowledgeIngestResponse(
                            success=False,
                            document_id=doc_id,
                            chunk_count=chunk_count,
                            message=f"索引失败: {index_result.error}",
                        )
                    chunk_count = index_result.chunk_count
                    logger.info(f"索引完成: {chunk_count} vectors")
            else:
                # 无 Processor 时直接用 Document content 作为单个 chunk
                if self._indexing:
                    from document.model import Document as DocModel
                    chunk_count = 1

            # 更新计数器
            self._doc_count += 1
            self._chunk_count += chunk_count

            elapsed = round((time() - start) * 1000, 2)
            return KnowledgeIngestResponse(
                success=True,
                document_id=doc_id,
                chunk_count=chunk_count,
                message=f"摄入成功 ({elapsed}ms)",
            )

        except Exception as e:
            logger.error(f"知识库摄入失败: {type(e).__name__}: {e}")
            return KnowledgeIngestResponse(
                success=False,
                message=f"摄入异常: {type(e).__name__}: {e}",
            )

    def status(self) -> KnowledgeStatusResponse:
        """获取知识库当前状态。

        Returns:
            KnowledgeStatusResponse（含文档数 / Chunk 数 / 向量库状态）。
        """
        vs_status = "unknown"
        try:
            from retrieval.vectorstore.service import VectorStoreService
            from core.registry import _registry
            _ = _registry.get("vectorstore", None)
            vs_status = "connected" if _ is not None else "not_available"
        except Exception:
            vs_status = "error"

        return KnowledgeStatusResponse(
            total_documents=self._doc_count,
            total_chunks=self._chunk_count,
            vectorstore=vs_status,
        )
