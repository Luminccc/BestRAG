"""Knowledge Base Scenario — 验证知识库摄入全流程。

流程::

    临时测试文档 → KnowledgeBaseService.ingest() → 状态检查

验证内容：
- 文件解析
- Document 生成
- Chunk 切分
- Embedding 生成
- Vector 写入
- 状态更新
"""

import tempfile
from pathlib import Path
from time import time
from typing import Optional

from validation.model import ScenarioResult, CheckResult, ValidationStatus

# 测试文档内容
_TEST_CONTENT = (
    "# BestRAG 知识库测试文档\n\n"
    "## 简介\n"
    "BestRAG 是一个企业级 RAG 框架，支持 PDF、DOCX、Markdown 等多种文档格式。\n"
    "它使用 Milvus 作为向量数据库，BGE-M3 作为嵌入模型。\n\n"
    "## 安装\n"
    "需要 Python 3.10+，使用 uv sync 安装依赖。\n\n"
    "## 部署\n"
    "配置 Milvus 连接和 LLM API Key 后，执行 uvicorn main:app --reload 启动。\n"
)


def run_knowledge_base_scenario(kb_service=None) -> ScenarioResult:
    """执行知识库摄入场景验证。

    Args:
        kb_service: KnowledgeBaseService 实例。

    Returns:
        ScenarioResult（含各步骤检查项）。
    """
    name = "knowledge_base"
    checks: list[CheckResult] = []
    start = time()
    test_path: Optional[str] = None

    if kb_service is None:
        return ScenarioResult(
            name=name,
            status=ValidationStatus.SKIP,
            checks=[CheckResult(name=name, status=ValidationStatus.SKIP, message="KnowledgeBaseService 未注入")],
        )

    try:
        # ── Step 1: 创建测试文档 ──
        t0 = time()
        f = tempfile.NamedTemporaryFile(suffix=".md", mode="w", encoding="utf-8", delete=False)
        f.write(_TEST_CONTENT)
        f.close()
        test_path = f.name
        checks.append(CheckResult(
            name="create_doc",
            status=ValidationStatus.PASS,
            message=f"测试文档已创建: {len(_TEST_CONTENT)} chars",
            latency=round((time() - t0) * 1000, 2),
        ))

        # ── Step 2: 执行 ingest ──
        t0 = time()
        from features.model import KnowledgeIngestRequest
        req = KnowledgeIngestRequest(file_path=test_path, strategy="recursive")
        result = kb_service.ingest(req)
        ingest_latency = round((time() - t0) * 1000, 2)

        if result.success:
            checks.append(CheckResult(
                name="ingest",
                status=ValidationStatus.PASS,
                message=f"摄入成功: {result.chunk_count} chunks, {result.document_id}",
                latency=ingest_latency,
                details={"document_id": result.document_id, "chunk_count": result.chunk_count},
            ))
        else:
            checks.append(CheckResult(
                name="ingest",
                status=ValidationStatus.FAIL,
                message=f"摄入失败: {result.message}",
                latency=ingest_latency,
            ))
            return _build_result(name, checks, start)

        # ── Step 3: 状态检查 ──
        t0 = time()
        status = kb_service.status()
        checks.append(CheckResult(
            name="status",
            status=ValidationStatus.PASS if status.total_documents > 0 else ValidationStatus.FAIL,
            message=f"文档: {status.total_documents}, Chunks: {status.total_chunks}, VS: {status.vectorstore}",
            latency=round((time() - t0) * 1000, 2),
            details={"total_documents": status.total_documents, "total_chunks": status.total_chunks},
        ))

        return _build_result(name, checks, start)

    except Exception as e:
        checks.append(CheckResult(
            name=name,
            status=ValidationStatus.FAIL,
            message=f"场景异常: {type(e).__name__}: {e}",
        ))
        return _build_result(name, checks, start)

    finally:
        if test_path:
            Path(test_path).unlink(missing_ok=True)


def _build_result(name: str, checks: list[CheckResult], start: float) -> ScenarioResult:
    duration = round(time() - start, 3)
    fail_count = sum(1 for c in checks if c.status == ValidationStatus.FAIL)
    return ScenarioResult(
        name=name,
        status=ValidationStatus.FAIL if fail_count > 0 else ValidationStatus.PASS,
        duration=duration,
        checks=checks,
    )
