"""Generation Check — 验证 Generation 管线完整性。

流程：
    Mock RetrievalResult → ContextBuilder → PromptBuilder → LLM Pipeline → Answer

检查项：
1. ContextBuilder 构建是否正常
2. PromptBuilder 构建是否正常
3. Generation Pipeline 是否正常产出回答

默认 SKIP（需设置环境变量 BESTRAG_VALIDATION_LLM=true 启用）。
"""

import os
from time import time

from validation.model import ValidationReport, CheckResult, ValidationStatus

# 测试用 Sample Document
_SAMPLE_CONTENT = (
    "BestRAG 是一个企业级 RAG（Retrieval-Augmented Generation）框架。"
    "它支持多种文档格式，包括 PDF、DOCX、Markdown 和 TXT。"
    "BestRAG 使用 Milvus 作为向量数据库，BGE-M3 作为嵌入模型。"
    "部署 BestRAG 需要 Python 3.10+ 环境。"
)

_SAMPLE_QUERY = "如何部署 BestRAG？"


def check_generation(generation_service=None) -> ValidationReport:
    """验证 Generation Pipeline 完整性。

    Args:
        generation_service: GenerationService 实例。

    Returns:
        包含子检查项的 ValidationReport。
    """
    start = time()
    module = "generation"
    checks: list[CheckResult] = []

    # ── 环境变量开关 ──
    llm_enabled = os.environ.get("BESTRAG_VALIDATION_LLM", "").lower() in ("1", "true", "yes")
    if not llm_enabled:
        checks.append(CheckResult(
            name="generation_enabled",
            status=ValidationStatus.SKIP,
            message="Generation 验证未启用（设置 BESTRAG_VALIDATION_LLM=true 启用）",
        ))
        return ValidationReport.from_checks(module, checks).complete(start)

    if generation_service is None:
        checks.append(CheckResult(
            name="service",
            status=ValidationStatus.SKIP,
            message="GenerationService 未注入",
        ))
        return ValidationReport.from_checks(module, checks, message="GenerationService 未注入").complete(start)

    # ── 检查 1：ContextBuilder ──
    try:
        from generation.context.builder import ContextBuilder

        # 构造 Mock RetrievalResult
        from retrieval.retriever.model import RetrievalResult as RR
        mock_results = [
            RR(chunk_id="c1", score=0.95, content=_SAMPLE_CONTENT, metadata={"source": "test"}),
        ]

        builder = ContextBuilder(max_length=2000)
        context = builder.build(mock_results)

        if not context:
            checks.append(CheckResult(
                name="context_builder",
                status=ValidationStatus.FAIL,
                message="ContextBuilder 返回空上下文",
            ))
        elif "[Document 1]" not in context:
            checks.append(CheckResult(
                name="context_builder",
                status=ValidationStatus.FAIL,
                message="ContextBuilder 输出格式异常",
                details={"preview": context[:200]},
            ))
        else:
            checks.append(CheckResult(
                name="context_builder",
                status=ValidationStatus.PASS,
                message=f"ContextBuilder 正常: {len(context)} chars",
                details={"preview": context[:100]},
            ))
    except Exception as e:
        checks.append(CheckResult(
            name="context_builder",
            status=ValidationStatus.FAIL,
            message=f"ContextBuilder 异常: {type(e).__name__}: {e}",
        ))

    # ── 检查 2：PromptBuilder ──
    try:
        from generation.prompt.builder import PromptBuilder

        pb = PromptBuilder()
        messages = pb.build(_SAMPLE_QUERY, context if "context" in dir() else "test context")

        if not messages or len(messages) < 2:
            checks.append(CheckResult(
                name="prompt_builder",
                status=ValidationStatus.FAIL,
                message=f"PromptBuilder 消息列表不完整: 只有 {len(messages)} 条",
            ))
        else:
            has_system = any(m["role"] == "system" for m in messages)
            has_user = any(m["role"] == "user" for m in messages)
            if has_system and has_user:
                checks.append(CheckResult(
                    name="prompt_builder",
                    status=ValidationStatus.PASS,
                    message=f"PromptBuilder 正常: {len(messages)} messages",
                    details={"roles": [m["role"] for m in messages]},
                ))
            else:
                checks.append(CheckResult(
                    name="prompt_builder",
                    status=ValidationStatus.FAIL,
                    message=f"PromptBuilder 缺少必要角色: system={has_system}, user={has_user}",
                ))
    except Exception as e:
        checks.append(CheckResult(
            name="prompt_builder",
            status=ValidationStatus.FAIL,
            message=f"PromptBuilder 异常: {type(e).__name__}: {e}",
        ))

    # ── 检查 3：Generation Pipeline ──
    try:
        t0 = time()
        response = generation_service.generate(
            query=_SAMPLE_QUERY,
            context=_SAMPLE_CONTENT,
        )
        latency = round((time() - t0) * 1000, 2)

        if response.answer and len(response.answer.strip()) > 0:
            checks.append(CheckResult(
                name="pipeline",
                status=ValidationStatus.PASS,
                message=f"Generation Pipeline 正常: {len(response.answer)} chars",
                latency=latency,
                details={
                    "answer_preview": response.answer[:200],
                    "model": response.model,
                    "sources_count": len(response.sources),
                },
            ))
        else:
            checks.append(CheckResult(
                name="pipeline",
                status=ValidationStatus.FAIL,
                message="Generation Pipeline 返回空回答",
                latency=latency,
            ))
    except Exception as e:
        checks.append(CheckResult(
            name="pipeline",
            status=ValidationStatus.FAIL,
            message=f"Generation Pipeline 异常: {type(e).__name__}: {e}",
        ))

    return ValidationReport.from_checks(module, checks).complete(start)
