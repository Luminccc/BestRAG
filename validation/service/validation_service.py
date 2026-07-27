"""ValidationService — 验证流程编排层。

职责：
- 编排单文件验证（POST /validation/document）
- 编排全量回归验证（POST /validation/document/all）
- 编排 Generation / RAG Flow / Chat 验证（V2）
- 不包含任何业务逻辑
"""

from time import time
from pathlib import Path
import tempfile
from typing import Optional

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
from validation.model import ValidationReport, ChatResult, StatusResult, CheckResult, ValidationStatus, ScenarioResult, DebugResult


class ValidationService:
    """验证服务 — 对 Document/Processor/Retrieval/Generation 链路执行完整性检查。

    Usage::

        svc = ValidationService(
            document_service, processor_service, chunk_service,
            embedding_service, vector_store_service, retrieval_service, rerank_service,
            generation_service,
        )
        # V1 checks
        doc_report = svc.validate_document("/data/test.pdf")
        # V2 checks
        llm_report = svc.validate_llm()
        gen_report = svc.validate_generation()
        rag_report = svc.validate_rag_flow()
        chat_result = svc.run_chat_test("如何部署?")
    """

    def __init__(
        self,
        document_service: DocumentService,
        processor_service=None,    # ProcessorService | None
        chunk_service=None,         # ChunkService | None
        transformer_service=None,   # TransformerService | None
        embedding_service=None,     # EmbeddingService | None
        vector_store_service=None,  # VectorStoreService | None
        retrieval_service=None,     # RetrievalService | None
        rerank_service=None,        # RerankService | None
        generation_service=None,    # GenerationService | None (V2)
    ):
        self._doc_service = document_service
        self._processor_service = processor_service
        self._chunk_service = chunk_service
        self._transformer_service = transformer_service
        self._embedding_service = embedding_service
        self._vector_store_service = vector_store_service
        self._retrieval_service = retrieval_service
        self._rerank_service = rerank_service
        self._generation_service = generation_service

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

    # ---- V2: Generation 验证方法 ----

    def validate_llm(self) -> ValidationReport:
        """验证 LLM Provider 是否正常。"""
        from validation.checks.llm_check import check_llm
        return check_llm(self._generation_service)

    def validate_generation(self) -> ValidationReport:
        """验证 Generation 链路：Context → Prompt → LLM。"""
        from validation.checks.generation_check import check_generation
        return check_generation(self._generation_service)

    def validate_rag_flow(self) -> ValidationReport:
        """验证完整 RAG Flow：Document → Answer。"""
        from validation.integration.rag_flow import run_rag_flow
        return run_rag_flow(
            doc_service=self._doc_service,
            processor_service=self._processor_service,
            embedding_service=self._embedding_service,
            vector_store_service=self._vector_store_service,
            retrieval_service=self._retrieval_service,
            generation_service=self._generation_service,
        )

    # ---- V2: Scenario 验证方法 ----

    def validate_knowledge_base_scenario(self) -> "ScenarioResult":
        """验证 KnowledgeBase 场景：文档摄入 → 索引。"""
        from validation.scenarios.knowledge_base import run_knowledge_base_scenario
        from core.application import bootstrap
        _app = bootstrap()
        kb_svc = _app.context.services.get("knowledge_base")
        return run_knowledge_base_scenario(kb_svc)

    def validate_qa_scenario(self) -> "ScenarioResult":
        """验证 QA 场景：提问 → 检索 → 生成 → 回答。"""
        from validation.scenarios.qa import run_qa_scenario
        from core.application import bootstrap
        _app = bootstrap()
        qa_svc = _app.context.services.get("qa")
        return run_qa_scenario(qa_svc)

    def validate_rag_e2e_scenario(self) -> "ScenarioResult":
        """验证 RAG E2E 场景：文档 → 索引 → 问答 → 验证。"""
        from validation.scenarios.rag_e2e import run_rag_e2e_scenario
        from core.application import bootstrap
        _app = bootstrap()
        kb_svc = _app.context.services.get("knowledge_base")
        qa_svc = _app.context.services.get("qa")
        return run_rag_e2e_scenario(kb_svc, qa_svc)

    # ---- V2: Diagnostics 方法 ----

    def debug_retrieval(self, query: str) -> "DebugResult":
        """诊断检索流程。"""
        from validation.diagnostics import debug_retrieval as _debug_retrieval
        return _debug_retrieval(
            query=query,
            retrieval_service=self._retrieval_service,
            embedding_service=self._embedding_service,
            vector_store_service=self._vector_store_service,
            rerank_service=self._rerank_service,
        )

    def debug_generation(self, query: str) -> "DebugResult":
        """诊断生成流程。"""
        from validation.diagnostics import debug_generation as _debug_generation
        return _debug_generation(
            query=query,
            generation_service=self._generation_service,
            retrieval_service=self._retrieval_service,
            rerank_service=self._rerank_service,
        )

    def run_chat_test(self, query: str, use_test_data: bool = False) -> ChatResult:
        """执行 Chat 验证：Query → Retrieval → Generation → Answer。

        Args:
            query:         用户问题。
            use_test_data: 是否自动生成测试数据并索引。

        Returns:
            ChatResult（含 answer / sources / latency）。
        """
        from validation.integration.chat_flow import run_chat_flow
        return run_chat_flow(
            query=query,
            retrieval_service=self._retrieval_service,
            generation_service=self._generation_service,
            embedding_service=self._embedding_service,
            vector_store_service=self._vector_store_service,
            doc_service=self._doc_service,
            processor_service=self._processor_service,
            use_test_data=use_test_data,
        )

    def get_system_status(self) -> "StatusResult":
        """获取系统状态快照。"""
        from validation.integration.chat_flow import get_status
        return get_status(
            embedding_service=self._embedding_service,
            vector_store_service=self._vector_store_service,
            retrieval_service=self._retrieval_service,
            rerank_service=self._rerank_service,
            generation_service=self._generation_service,
        )

    def run_full_validation(self) -> ValidationReport:
        """执行全链路验证（含 Generation）。"""
        import os
        from validation.model import CheckResult, ValidationStatus

        checks: list[CheckResult] = []

        # 1) LLM Check（默认 SKIP，需环境变量启用）
        llm_enabled = os.environ.get("BESTRAG_VALIDATION_LLM", "").lower() in ("1", "true", "yes")
        if llm_enabled:
            try:
                report = self.validate_llm()
                for c in report.checks:
                    checks.append(c)
            except Exception as e:
                checks.append(CheckResult(
                    name="llm",
                    status=ValidationStatus.FAIL,
                    message=f"LLM 验证异常: {e}",
                ))
        else:
            checks.append(CheckResult(
                name="llm",
                status=ValidationStatus.SKIP,
                message="LLM 验证未启用（设置 BESTRAG_VALIDATION_LLM=true 启用）",
            ))

        # 2) Generation Check
        if self._generation_service and llm_enabled:
            try:
                report = self.validate_generation()
                for c in report.checks:
                    checks.append(c)
            except Exception as e:
                checks.append(CheckResult(
                    name="generation",
                    status=ValidationStatus.FAIL,
                    message=f"Generation 验证异常: {e}",
                ))
        elif not llm_enabled:
            checks.append(CheckResult(
                name="generation",
                status=ValidationStatus.SKIP,
                message="Generation 验证未启用（需 LLM）",
            ))
        else:
            checks.append(CheckResult(
                name="generation",
                status=ValidationStatus.SKIP,
                message="GenerationService 未注入",
            ))

        # 3) Embedding Check
        if self._embedding_service:
            try:
                report = self.validate_embedding()
                checks.append(_report_to_check(report))
            except Exception as e:
                checks.append(CheckResult(name="embedding", status=ValidationStatus.FAIL, message=str(e)))
        else:
            checks.append(CheckResult(name="embedding", status=ValidationStatus.SKIP, message="EmbeddingService 未注入"))

        # 4) VectorStore Check
        if self._vector_store_service and self._embedding_service:
            try:
                report = self.validate_vectorstore()
                checks.append(_report_to_check(report))
            except Exception as e:
                checks.append(CheckResult(name="vectorstore", status=ValidationStatus.FAIL, message=str(e)))
        else:
            checks.append(CheckResult(name="vectorstore", status=ValidationStatus.SKIP, message="VectorStoreService 未注入"))

        # 5) Retrieval Check
        if self._retrieval_service and self._vector_store_service and self._embedding_service:
            try:
                report = self.validate_retrieval()
                checks.append(_report_to_check(report))
            except Exception as e:
                checks.append(CheckResult(name="retrieval", status=ValidationStatus.FAIL, message=str(e)))
        else:
            checks.append(CheckResult(name="retrieval", status=ValidationStatus.SKIP, message="RetrievalService 未注入"))

        return ValidationReport.from_checks("full_validation", checks)


def _report_to_check(report: ValidationReport) -> CheckResult:
    """将 V1 ValidationReport 转为 CheckResult。"""
    from validation.model import ValidationStatus, CheckResult
    return CheckResult(
        name=report.module,
        status=ValidationStatus.PASS if report.status == "success" else ValidationStatus.FAIL,
        message=report.message or "",
        latency=report.duration_ms,
        details=report.details,
    )


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