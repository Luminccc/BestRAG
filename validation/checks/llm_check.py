"""LLM Check — 验证 LLM Provider 是否正常运行。

检查项：
1. provider 初始化是否成功
2. API Key 是否配置
3. Model 是否可达
4. 基本 Response 是否正常

默认 SKIP（需设置环境变量 BESTRAG_VALIDATION_LLM=true 启用）。
"""

import os
from time import time

from validation.model import ValidationReport, CheckResult, ValidationStatus


def check_llm(generation_service=None) -> ValidationReport:
    """验证 LLM Provider 完整性。

    Args:
        generation_service: GenerationService 实例（可选）。

    Returns:
        包含子检查项的 ValidationReport。
    """
    start = time()
    module = "llm"
    checks: list[CheckResult] = []

    # ── 检查 1：环境变量开关 ──
    llm_enabled = os.environ.get("BESTRAG_VALIDATION_LLM", "").lower() in ("1", "true", "yes")
    if not llm_enabled:
        checks.append(CheckResult(
            name="llm_enabled",
            status=ValidationStatus.SKIP,
            message="LLM 验证未启用（设置 BESTRAG_VALIDATION_LLM=true 启用）",
        ))
        return ValidationReport.from_checks(module, checks).complete(start)

    # ── 检查 2：Config 读取 ──
    from core.config import get_config

    try:
        cfg = get_config().generation
    except Exception as e:
        checks.append(CheckResult(
            name="config",
            status=ValidationStatus.FAIL,
            message=f"生成配置读取失败: {e}",
        ))
        return ValidationReport.from_checks(module, checks, message="配置读取失败").complete(start)

    # ── 检查 3：API Key ──
    api_key = cfg.api_key or os.environ.get("BESTRAG_LLM_API_KEY", "")
    if not api_key:
        checks.append(CheckResult(
            name="api_key",
            status=ValidationStatus.FAIL,
            message="LLM API Key 未配置（请设置 BESTRAG_LLM_API_KEY 环境变量或 config.yaml 中 generation.api_key）",
        ))
        return ValidationReport.from_checks(module, checks, message="API Key 缺失").complete(start)
    checks.append(CheckResult(
        name="api_key",
        status=ValidationStatus.PASS,
        message="API Key 已配置",
        details={"key_prefix": api_key[:8] + "..." if len(api_key) > 8 else "***"},
    ))

    # ── 检查 4：Provider 初始化 ──
    try:
        from generation.provider.openai_compatible import OpenAICompatibleProvider
        provider = OpenAICompatibleProvider()
        checks.append(CheckResult(
            name="provider_init",
            status=ValidationStatus.PASS,
            message=f"Provider 初始化成功: {cfg.model_name}",
            details={"model": cfg.model_name, "base_url": cfg.base_url},
        ))
    except Exception as e:
        checks.append(CheckResult(
            name="provider_init",
            status=ValidationStatus.FAIL,
            message=f"Provider 初始化失败: {e}",
        ))
        return ValidationReport.from_checks(module, checks, message="Provider 初始化失败").complete(start)

    # ── 检查 5：基本 Response ──
    try:
        t0 = time()
        answer = provider.generate([
            {"role": "system", "content": "你是一个测试助手，请简短回复。"},
            {"role": "user", "content": "回复 OK"},
        ])
        latency = round((time() - t0) * 1000, 2)

        if answer and len(answer.strip()) > 0:
            checks.append(CheckResult(
                name="response",
                status=ValidationStatus.PASS,
                message=f"LLM 响应正常 ({len(answer)} chars)",
                latency=latency,
                details={"answer_preview": answer[:100], "model": cfg.model_name},
            ))
        else:
            checks.append(CheckResult(
                name="response",
                status=ValidationStatus.FAIL,
                message="LLM 返回空响应",
                latency=latency,
            ))
    except Exception as e:
        checks.append(CheckResult(
            name="response",
            status=ValidationStatus.FAIL,
            message=f"LLM 调用失败: {type(e).__name__}: {e}",
        ))

    return ValidationReport.from_checks(module, checks).complete(start)
