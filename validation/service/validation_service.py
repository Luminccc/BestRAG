"""ValidationService — 验证流程编排层。

职责：
- 编排单文件验证（POST /validation/document）
- 编排全量回归验证（POST /validation/document/all）
- 不包含任何业务逻辑
"""

from time import time
from pathlib import Path
import tempfile

from document.service import DocumentService
from document.dispatcher import UnsupportedFileTypeError
from document.model import Document

from retrieval.embedding.service import EmbeddingService
from retrieval.vectorstore.service import VectorStoreService
from retrieval.retriever.service import RetrievalService
from retrieval.reranker.service import RerankService

from validation.checks.chunk_check import check_chunk
from validation.checks.document_check import check_document
from validation.checks.pipeline_check import check_pipeline
from validation.checks.processor_check import check_cleaner
from validation.checks.transformer_check import check_transformer
from validation.checks.embedding_check import check_embedding
from validation.checks.vectorstore_check import check_vectorstore
from validation.checks.retrieval_check import check_retrieval
from validation.checks.rerank_check import check_rerank
from validation.model import ValidationReport


class ValidationService:
    """验证服务 — 对 Document/Processor/Retrieval 链路执行完整性检查。

    Usage::

        svc = ValidationService(document_service, processor_service, chunk_service,
                               embedding_service, vector_store_service, retrieval_service, rerank_service)
        doc_report = svc.validate_document("/data/test.pdf")
        clean_report = svc.validate_cleaner("/data/test.pdf")
        chunk_report = svc.validate_chunker("/data/test.pdf", "recursive")
        pipe_report = svc.validate_pipeline("/data/test.pdf", "recursive")
        embedding_report = svc.validate_embedding()
        vectorstore_report = svc.validate_vectorstore()
        retrieval_report = svc.validate_retrieval()
        rerank_report = svc.validate_rerank()
        all_reports = svc.validate_all()
    """

    def __init__(
        self,
        document_service: DocumentService,
        processor_service=None,   # ProcessorService | None
        chunk_service=None,        # ChunkService | None
        transformer_service=None,  # TransformerService | None
        embedding_service=None,    # EmbeddingService | None
        vector_store_service=None, # VectorStoreService | None
        retrieval_service=None,    # RetrievalService | None
        rerank_service=None,       # RerankService | None
    ):
        self._doc_service = document_service
        self._processor_service = processor_service
        self._chunk_service = chunk_service
        self._transformer_service = transformer_service
        self._embedding_service = embedding_service
        self._vector_store_service = vector_store_service
        self._retrieval_service = retrieval_service
        self._rerank_service = rerank_service

    # ---- 单文件验证 ----

    def validate_document(self, file_path: str) -> ValidationReport:
        """验证单个文件的 Document 链路是否正常。

        流程：
            DocumentService.create_document(file_path)
                → DocumentCheck 逐项检查
                → ValidationReport
        """
        parser_name: str | None = None
        doc: Document | None = None

        # 执行 DocumentService
        doc = self._doc_service.create_document(file_path)
        parser_name = _resolve_parser_name(file_path)

        # 执行 DocumentCheck
        return check_document(doc, parser_name=parser_name)

    # ---- Cleaner 验证 ----

    def validate_cleaner(self, file_path: str) -> ValidationReport:
        """验证 Cleaner 链路：Document → Cleaner → Clean Document。

        流程：
            DocumentService.create_document(file_path)
                → ProcessorService.process(document)
                → check_cleaner(clean_doc)
                → ValidationReport

        Raises:
            RuntimeError: 如果 ProcessorService 未注入。
        """
        if self._processor_service is None:
            raise RuntimeError(
                "ProcessorService 未注入，请在 main.py 中传递 processor_service 参数"
            )

        # 1) 生成 Document
        doc = self._doc_service.create_document(file_path)

        # 2) 执行 Cleaner（取 ProcessedDocument.document）
        processed = self._processor_service.process(doc)

        # 3) 验证清洗结果
        return check_cleaner(processed.document)

    # ---- Chunk 验证 ----

    def validate_chunker(self, file_path: str, strategy: str) -> ValidationReport:
        """验证 Chunk 链路：Clean Document → ChunkService → Chunk[]。

        流程：
            DocumentService.create_document(file_path)
                → ProcessorService.process(document)
                → ChunkService.chunk(clean_doc, strategy)
                → check_chunk(chunks)
                → ValidationReport

        Args:
            file_path: 文件路径。
            strategy:  切分策略名（"fixed" / "recursive"）。

        Raises:
            RuntimeError: ProcessorService 或 ChunkService 未注入。
        """
        if self._processor_service is None:
            raise RuntimeError(
                "ProcessorService 未注入，请在 main.py 中传递 processor_service 参数"
            )
        if self._chunk_service is None:
            raise RuntimeError(
                "ChunkService 未注入，请在 main.py 中传递 chunk_service 参数"
            )

        # 1) 生成 + 清洗 Document
        doc = self._doc_service.create_document(file_path)
        processed = self._processor_service.process(doc)

        # 2) 执行 Chunk 策略
        chunks = self._chunk_service.chunk(processed.document, strategy)

        # 3) 验证 Chunk 结果
        return check_chunk(chunks, document_id=processed.document.id, strategy=strategy)

    # ---- Transformer 验证 ----

    def validate_transformer(self, file_path: str) -> ValidationReport:
        """验证 Transformer 链路：Document → Transformer → Normalized Document。

        流程：
            DocumentService.create_document(file_path)
                → ProcessorService.process(document)
                → TransformerService.transform(clean_doc)
                → check_transformer(normalized_doc)
                → ValidationReport

        Raises:
            RuntimeError: TransformerService 未注入。
        """
        if self._processor_service is None:
            raise RuntimeError("ProcessorService 未注入")
        if self._transformer_service is None:
            raise RuntimeError(
                "TransformerService 未注入，请在 main.py 中传递 transformer_service 参数"
            )

        # 1) 生成 + 清洗 Document
        doc = self._doc_service.create_document(file_path)
        processed = self._processor_service.process(doc)

        # 2) 执行 Transformer（取 ProcessedDocument.document）
        normalized = self._transformer_service.transform(processed.document)

        # 3) 验证标准化结果
        return check_transformer(normalized)

    # ---- Pipeline 验证 ----

    def validate_pipeline(self, file_path: str, strategy: str = "recursive") -> ValidationReport:
        """验证完整 Pipeline：Document → Cleaner → Chunker → Transformer。

        流程：
            DocumentService.create_document(file_path)
                → ProcessorService.process(document, strategy)
                → check_pipeline(processed)
                → ValidationReport

        Raises:
            RuntimeError: ProcessorService 未注入（旧的简单模式）。
        """
        if self._processor_service is None:
            raise RuntimeError("ProcessorService 未注入")

        # 1) 生成 Document
        doc = self._doc_service.create_document(file_path)

        # 2) 执行完整 Pipeline
        processed = self._processor_service.process(doc, strategy)

        # 3) 验证 Pipeline 结果
        return check_pipeline(processed, strategy=strategy)

    # ---- 全量回归验证 ----

    def validate_all(self) -> list[ValidationReport]:
        """执行全量回归验证。

        自动生成测试文件，覆盖：
        - 4 种受支持格式（txt / md / pdf / docx）
        - 3 种异常场景（unsupported / not_found / empty）

        Returns:
            所有验证结果的列表（每个场景一条）。
        """
        results: list[ValidationReport] = []

        with _TestFileGenerator() as gen:
            # ---- 成功场景 ----
            for label, path in [
                ("txt", gen.txt()),
                ("md", gen.md()),
                ("pdf", gen.pdf()),
                ("docx", gen.docx()),
            ]:
                report = self._safe_validate(label, path)
                results.append(report)

            # ---- 异常场景 ----
            # 不支持的类型
            results.append(self._safe_validate("unsupported", gen.unsupported()))
            # 文件不存在
            results.append(self._safe_validate("not_found", gen.not_found()))
            # 空文件
            results.append(self._safe_validate("empty", gen.empty_txt()))

        return results

    # ---- 内部 ----

    def _safe_validate(self, label: str, file_path: str) -> ValidationReport:
        """安全执行单次验证，捕获预期异常并转为 ValidationReport。"""
        start = time()

        if label == "unsupported":
            try:
                self._doc_service.create_document(file_path)
                return ValidationReport.fail(
                    "document",
                    message="预期 UnsupportedFileTypeError 但未抛出",
                    test_case=label,
                    file_path=file_path,
                ).complete(start)
            except UnsupportedFileTypeError:
                return ValidationReport.ok(
                    "document",
                    test_case=label,
                    file_path=file_path,
                    expected_error="UnsupportedFileTypeError",
                ).complete(start)
            except Exception as e:
                return ValidationReport.fail(
                    "document",
                    message=f"预期 UnsupportedFileTypeError，实际异常: {type(e).__name__}",
                    test_case=label,
                ).complete(start)

        if label == "not_found":
            try:
                self._doc_service.create_document(file_path)
                return ValidationReport.fail(
                    "document",
                    message="预期 FileNotFoundError 但未抛出",
                    test_case=label,
                    file_path=file_path,
                ).complete(start)
            except FileNotFoundError:
                return ValidationReport.ok(
                    "document",
                    test_case=label,
                    file_path=file_path,
                    expected_error="FileNotFoundError",
                ).complete(start)
            except Exception as e:
                return ValidationReport.fail(
                    "document",
                    message=f"预期 FileNotFoundError，实际异常: {type(e).__name__}",
                    test_case=label,
                ).complete(start)

        # 正常验证
        try:
            doc = self._doc_service.create_document(file_path)
            report = check_document(doc, parser_name=_resolve_parser_name(file_path))
            report.details["test_case"] = label
            report.details["file_path"] = file_path
            return report.complete(start)
        except Exception as e:
            return ValidationReport.fail(
                "document",
                message=f"验证异常: {type(e).__name__}: {e}",
                test_case=label,
                file_path=file_path,
            ).complete(start)

    # ---- Retrieval 验证方法 ----

    def validate_embedding(self) -> ValidationReport:
        """验证 Embedding 链路是否正常。"""
        if self._embedding_service is None:
            raise RuntimeError("EmbeddingService 未注入，请在 main.py 中传递 embedding_service 参数")
        return check_embedding(self._embedding_service)

    def validate_vectorstore(self) -> ValidationReport:
        """验证 VectorStore 链路是否正常。"""
        if self._vector_store_service is None:
            raise RuntimeError("VectorStoreService 未注入")
        if self._embedding_service is None:
            raise RuntimeError("EmbeddingService 未注入")
        return check_vectorstore(self._vector_store_service, self._embedding_service)

    def validate_retrieval(self) -> ValidationReport:
        """验证 Retrieval 链路是否正常。"""
        if self._retrieval_service is None:
            raise RuntimeError("RetrievalService 未注入")
        if self._vector_store_service is None:
            raise RuntimeError("VectorStoreService 未注入")
        if self._embedding_service is None:
            raise RuntimeError("EmbeddingService 未注入")
        return check_retrieval(self._retrieval_service, self._vector_store_service, self._embedding_service)

    def validate_rerank(self) -> ValidationReport:
        """验证 Rerank 链路是否正常。"""
        if self._rerank_service is None:
            raise RuntimeError("RerankService 未注入")
        return check_rerank(self._rerank_service)


class _TestFileGenerator:
    """临时测试文件生成器，作为上下文管理器使用。"""
    def __init__(self):
        self._files: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        for path in self._files:
            Path(path).unlink(missing_ok=True)

    def _tmp(self, suffix: str, content: bytes = b"") -> str:
        f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        if content:
            f.write(content)
        f.close()
        self._files.append(f.name)
        return f.name

    def txt(self) -> str:
        return self._tmp(".txt", "BestRAG validation test content.\n第二行。".encode("utf-8"))

    def md(self) -> str:
        return self._tmp(".md", b"# Validation Test\n\nThis is a **markdown** file.")

    def pdf(self) -> str:
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 100), "BestRAG PDF validation test.")
        path = self._tmp(".pdf")
        doc.save(path)
        doc.close()
        return path

    def docx(self) -> str:
        from docx import Document as DocxDoc
        doc = DocxDoc()
        doc.add_paragraph("BestRAG DOCX validation test.")
        doc.add_paragraph("第二段。")
        path = self._tmp(".docx")
        doc.save(path)
        return path

    def unsupported(self) -> str:
        return self._tmp(".exe", b"not a supported format")

    def not_found(self) -> str:
        return "/not_exist_file_for_validation_test.pdf"

    def empty_txt(self) -> str:
        return self._tmp(".txt", b"")


def _resolve_parser_name(file_path: str) -> str:
    """根据文件路径推测 Provider 名称（仅用于报告）。"""
    ext = Path(file_path).suffix.lower()
    mapping = {
        ".txt": "MarkItDownProvider",
        ".md": "MarkItDownProvider",
        ".pdf": "OpenDataLoaderProvider",
        ".docx": "MarkItDownProvider",
        ".pptx": "MarkItDownProvider",
        ".xlsx": "MarkItDownProvider",
        ".html": "MarkItDownProvider",
    }
    return mapping.get(ext, "unknown")