"""RAG Flow Integration — 完整 RAG 流程验证。

流程::

    临时测试文档 → Parser → Processor → Indexing → Retrieval → Generation → Answer

用于验证整个系统闭环是否正常。
"""

from time import time
from pathlib import Path
import tempfile
from typing import Any

from validation.model import ValidationReport, CheckResult, ValidationStatus

# 测试文档内容
_TEST_CONTENT = (
    "# BestRAG 部署指南\n\n"
    "## 环境要求\n\n"
    "BestRAG 需要 Python 3.10 或更高版本。\n"
    "推荐使用虚拟环境安装依赖：\n\n"
    "```bash\n"
    "python -m venv .venv\n"
    "source .venv/bin/activate\n"
    "```\n\n"
    "## 安装步骤\n\n"
    "1. 克隆仓库\n"
    "2. 安装依赖：`uv sync` 或 `pip install -r requirements.txt`\n"
    "3. 配置 Milvus 连接地址\n"
    "4. 配置 LLM API Key\n"
    "5. 启动服务：`uvicorn main:app --reload`\n\n"
    "## 向量数据库\n\n"
    "使用 Milvus 作为向量数据库，默认连接 127.0.0.1:19530。\n"
    "本框架使用 BGE-M3 模型进行文本嵌入，维度为 1024。\n"
)

_TEST_QUERY = "如何安装 BestRAG？"


def run_rag_flow(
    doc_service=None,
    processor_service=None,
    embedding_service=None,
    vector_store_service=None,
    retrieval_service=None,
    generation_service=None,
) -> ValidationReport:
    """执行完整 RAG Flow 验证。

    自动生成临时测试文档，走完整流程并验证各环节。

    Args:
        doc_service:          DocumentService 实例。
        processor_service:    ProcessorService 实例。
        embedding_service:    EmbeddingService 实例。
        vector_store_service: VectorStoreService 实例。
        retrieval_service:    RetrievalService 实例。
        generation_service:   GenerationService 实例。

    Returns:
        包含各阶段检查项的 ValidationReport。
    """
    start = time()
    module = "rag_flow"
    checks: list[CheckResult] = []
    test_file_path: str | None = None

    try:
        # ── Step 1: 生成临时测试文档 ──
        t0 = time()
        test_file_path = _create_temp_doc()
        checks.append(CheckResult(
            name="create_test_doc",
            status=ValidationStatus.PASS,
            message=f"临时测试文档已创建: {Path(test_file_path).name}",
            latency=round((time() - t0) * 1000, 2),
        ))

        # ── Step 2: Document Parsing ──
        if doc_service is None:
            checks.append(CheckResult(name="document", status=ValidationStatus.SKIP, message="DocumentService 未注入"))
            return _build_result(module, checks, start)

        t0 = time()
        doc = doc_service.create_document(test_file_path)
        doc_latency = round((time() - t0) * 1000, 2)
        checks.append(CheckResult(
            name="document",
            status=ValidationStatus.PASS,
            message=f"文档解析成功: {len(doc.content)} chars",
            latency=doc_latency,
            details={"doc_id": doc.id, "content_len": len(doc.content)},
        ))

        # ── Step 3: Processor ──
        if processor_service is None:
            checks.append(CheckResult(name="processor", status=ValidationStatus.SKIP, message="ProcessorService 未注入"))
        else:
            t0 = time()
            try:
                processed = processor_service.process(doc, "recursive")
                proc_latency = round((time() - t0) * 1000, 2)
                chunk_count = len(processed.chunks) if hasattr(processed, "chunks") else 0
                checks.append(CheckResult(
                    name="processor",
                    status=ValidationStatus.PASS,
                    message=f"文档处理成功: {chunk_count} chunks",
                    latency=proc_latency,
                    details={"chunk_count": chunk_count},
                ))
            except Exception as e:
                checks.append(CheckResult(
                    name="processor",
                    status=ValidationStatus.FAIL,
                    message=f"文档处理失败: {type(e).__name__}: {e}",
                ))
                return _build_result(module, checks, start)

        # ── Step 4: Indexing ──
        indexing_ok = False
        if embedding_service is None:
            checks.append(CheckResult(name="indexing", status=ValidationStatus.SKIP, message="EmbeddingService 未注入"))
        elif vector_store_service is None:
            checks.append(CheckResult(name="indexing", status=ValidationStatus.SKIP, message="VectorStoreService 未注入"))
        elif processor_service is None:
            checks.append(CheckResult(name="indexing", status=ValidationStatus.SKIP, message="ProcessorService 未注入（无 chunk 数据）"))
        else:
            t0 = time()
            try:
                chunks = processed.chunks if hasattr(processed, "chunks") else []
                chunk_texts = [c.content if hasattr(c, "content") else str(c) for c in chunks]
                embeddings = embedding_service.embed_documents(chunk_texts)
                vectors = [e.vector for e in embeddings]
                ids = vector_store_service.add_texts(chunk_texts, vectors)
                idx_latency = round((time() - t0) * 1000, 2)
                indexing_ok = True
                checks.append(CheckResult(
                    name="indexing",
                    status=ValidationStatus.PASS,
                    message=f"索引成功: {len(ids)} vectors",
                    latency=idx_latency,
                    details={"vector_count": len(ids), "dim": embedding_service.dimension},
                ))
            except Exception as e:
                checks.append(CheckResult(
                    name="indexing",
                    status=ValidationStatus.FAIL,
                    message=f"索引失败: {type(e).__name__}: {e}",
                ))

        # ── Step 5: Retrieval ──
        if retrieval_service is None:
            checks.append(CheckResult(name="retrieval", status=ValidationStatus.SKIP, message="RetrievalService 未注入"))
        elif not indexing_ok:
            checks.append(CheckResult(name="retrieval", status=ValidationStatus.SKIP, message="Indexing 未完成，跳过检索"))
        else:
            t0 = time()
            try:
                results = retrieval_service.retrieve(_TEST_QUERY, top_k=3)
                ret_latency = round((time() - t0) * 1000, 2)
                checks.append(CheckResult(
                    name="retrieval",
                    status=ValidationStatus.PASS,
                    message=f"检索成功: {len(results)} results",
                    latency=ret_latency,
                    details={"result_count": len(results), "top_score": results[0].score if results else 0},
                ))
            except Exception as e:
                checks.append(CheckResult(
                    name="retrieval",
                    status=ValidationStatus.FAIL,
                    message=f"检索失败: {type(e).__name__}: {e}",
                ))

        # ── Step 6: Generation ──
        if generation_service is None:
            checks.append(CheckResult(name="generation", status=ValidationStatus.SKIP, message="GenerationService 未注入"))
        else:
            import os
            llm_enabled = os.environ.get("BESTRAG_VALIDATION_LLM", "").lower() in ("1", "true", "yes")
            if not llm_enabled:
                checks.append(CheckResult(name="generation", status=ValidationStatus.SKIP, message="LLM 未启用"))
            else:
                t0 = time()
                try:
                    context = "\n".join(r.content for r in results) if "results" in dir() and results else doc.content
                    response = generation_service.generate(query=_TEST_QUERY, context=context)
                    gen_latency = round((time() - t0) * 1000, 2)
                    checks.append(CheckResult(
                        name="generation",
                        status=ValidationStatus.PASS,
                        message=f"生成成功: {len(response.answer)} chars",
                        latency=gen_latency,
                        details={"answer_preview": response.answer[:200], "model": response.model},
                    ))
                except Exception as e:
                    checks.append(CheckResult(
                        name="generation",
                        status=ValidationStatus.FAIL,
                        message=f"生成失败: {type(e).__name__}: {e}",
                    ))

        return _build_result(module, checks, start)

    except Exception as e:
        checks.append(CheckResult(
            name="rag_flow",
            status=ValidationStatus.FAIL,
            message=f"RAG Flow 验证异常: {type(e).__name__}: {e}",
        ))
        return _build_result(module, checks, start)

    finally:
        # 清理临时文件
        if test_file_path:
            Path(test_file_path).unlink(missing_ok=True)


def _create_temp_doc() -> str:
    """创建临时测试 Markdown 文档。"""
    f = tempfile.NamedTemporaryFile(suffix=".md", mode="w", encoding="utf-8", delete=False)
    f.write(_TEST_CONTENT)
    f.close()
    return f.name


def _build_result(module: str, checks: list[CheckResult], start: float) -> ValidationReport:
    """构建最终报告。"""
    return ValidationReport.from_checks(module, checks).complete(start)
