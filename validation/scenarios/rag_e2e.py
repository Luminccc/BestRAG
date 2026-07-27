"""RAG E2E Scenario — 完整端到端验证。

流程::

    准备文档 → KnowledgeBase.ingest() → QA.ask() → 验证回答

验证知识库 → 问答的全链路闭环。
"""

import tempfile
from pathlib import Path
from time import time
from typing import Optional

from validation.model import ScenarioResult, CheckResult, ValidationStatus

# 完整测试文档
_TEST_CONTENT = (
    "# BestRAG 完整使用指南\n\n"
    "## 概述\n"
    "BestRAG 是一个企业级 RAG（Retrieval-Augmented Generation）框架，\n"
    "旨在为企业知识库提供高效的检索增强生成能力。\n\n"
    "## 系统要求\n"
    "- Python 3.10 或更高版本\n"
    "- Milvus 向量数据库（2.3+）\n"
    "- Redis（可选，用于缓存）\n"
    "- 8GB 以上内存\n\n"
    "## 安装步骤\n"
    "1. 克隆项目：git clone https://github.com/example/bestrag.git\n"
    "2. 进入目录：cd bestrag\n"
    "3. 创建虚拟环境：python -m venv .venv\n"
    "4. 激活环境：source .venv/bin/activate（Linux/Mac）或 .venv\\Scripts\\activate（Windows）\n"
    "5. 安装依赖：uv sync\n"
    "6. 配置 config.yaml 中的 Milvus 地址和 LLM API Key\n"
    "7. 启动服务：uvicorn main:app --reload\n\n"
    "## 验证安装\n"
    "访问 http://localhost:8000/static/validation.html 进入验证中心，\n"
    "检查系统状态和执行全链路验证。\n\n"
    "## 常见问题\n"
    "Q: Milvus 连接失败？\n"
    "A: 检查 config.yaml 中的 vectorstore.host 和 vectorstore.port 配置。\n\n"
    "Q: 如何切换 LLM？\n"
    "A: 修改 generation.base_url 和 generation.model_name，支持所有 OpenAI 兼容接口。\n"
)

_TEST_QUERY = "BestRAG 的系统要求是什么？"


def run_rag_e2e_scenario(kb_service=None, qa_service=None) -> ScenarioResult:
    """执行完整 RAG E2E 场景验证。

    流程：
        1. 创建测试文档
        2. KnowledgeBaseService.ingest() → 索引
        3. QAService.ask() → 回答
        4. 验证回答内容

    Args:
        kb_service: KnowledgeBaseService 实例。
        qa_service:  QAService 实例。

    Returns:
        ScenarioResult。
    """
    name = "rag_e2e"
    checks: list[CheckResult] = []
    start = time()
    test_path: Optional[str] = None

    if kb_service is None:
        return ScenarioResult(
            name=name,
            status=ValidationStatus.SKIP,
            checks=[CheckResult(name=name, status=ValidationStatus.SKIP, message="KnowledgeBaseService 未注入")],
        )
    if qa_service is None:
        return ScenarioResult(
            name=name,
            status=ValidationStatus.SKIP,
            checks=[CheckResult(name=name, status=ValidationStatus.SKIP, message="QAService 未注入")],
        )

    try:
        # ── Phase 1: 准备文档 ──
        t0 = time()
        f = tempfile.NamedTemporaryFile(suffix=".md", mode="w", encoding="utf-8", delete=False)
        f.write(_TEST_CONTENT)
        f.close()
        test_path = f.name
        checks.append(CheckResult(
            name="prepare",
            status=ValidationStatus.PASS,
            message=f"测试文档已准备: {len(_TEST_CONTENT)} chars",
            latency=round((time() - t0) * 1000, 2),
        ))

        # ── Phase 2: 知识库摄入 ──
        t0 = time()
        from features.model import KnowledgeIngestRequest
        req = KnowledgeIngestRequest(file_path=test_path, strategy="recursive")
        ingest_result = kb_service.ingest(req)
        ingest_latency = round((time() - t0) * 1000, 2)

        if not ingest_result.success:
            checks.append(CheckResult(
                name="ingest",
                status=ValidationStatus.FAIL,
                message=f"摄入失败: {ingest_result.message}",
                latency=ingest_latency,
            ))
            return _build_result(name, checks, start)

        checks.append(CheckResult(
            name="ingest",
            status=ValidationStatus.PASS,
            message=f"摄入成功: {ingest_result.chunk_count} chunks",
            latency=ingest_latency,
            details={"document_id": ingest_result.document_id, "chunk_count": ingest_result.chunk_count},
        ))

        # ── Phase 3: QA 问答 ──
        t0 = time()
        from features.model import QARequest
        qa_req = QARequest(query=_TEST_QUERY, top_k=5)
        qa_response = qa_service.ask(qa_req)
        qa_latency = round((time() - t0) * 1000, 2)

        sources = qa_response.sources or []
        checks.append(CheckResult(
            name="retrieval",
            status=ValidationStatus.PASS if len(sources) > 0 else ValidationStatus.FAIL,
            message=f"检索返回 {len(sources)} 条结果",
            latency=qa_response.retrieval_time,
            details={"source_count": len(sources)},
        ))

        answer = qa_response.answer or ""
        if not answer.strip():
            checks.append(CheckResult(
                name="generation",
                status=ValidationStatus.FAIL,
                message="回答为空",
                latency=qa_response.generation_time,
            ))
        elif answer.startswith("[") and ("错误" in answer or "失败" in answer):
            checks.append(CheckResult(
                name="generation",
                status=ValidationStatus.FAIL,
                message=f"生成异常: {answer[:100]}",
                latency=qa_response.generation_time,
            ))
        else:
            checks.append(CheckResult(
                name="generation",
                status=ValidationStatus.PASS,
                message=f"回答正常: {len(answer)} chars",
                latency=qa_response.generation_time,
                details={"answer_preview": answer[:200], "answer_length": len(answer)},
            ))

        # ── Phase 4: 验证答案内容 ──
        answer_lower = answer.lower()
        keywords = ["python", "milvus", "clone", "安装", "venv"]
        matched = [k for k in keywords if k.lower() in answer_lower]
        checks.append(CheckResult(
            name="content_check",
            status=ValidationStatus.PASS if len(matched) >= 2 else ValidationStatus.FAIL,
            message=f"关键词匹配: {len(matched)}/{len(keywords)} → {matched}",
            details={"matched_keywords": matched, "expected_keywords": keywords},
        ))

        return _build_result(name, checks, start)

    except Exception as e:
        checks.append(CheckResult(
            name=name,
            status=ValidationStatus.FAIL,
            message=f"E2E 场景异常: {type(e).__name__}: {e}",
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
