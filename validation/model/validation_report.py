"""ValidationReport — 验证结果统一数据协议。

所有 validation check 统一使用此模型输出。
使用 Pydantic v2 确保序列化和类型安全。

模型层次::

    ValidationReport
        ├── status: ValidationStatus (PASS / FAIL / SKIP)
        ├── summary: 概要信息（通过/失败/跳过计数）
        ├── checks: 子检查项列表 (CheckResult[])
        └── details: 扩展字段
"""

from enum import Enum
from time import time
from typing import Any, Optional

from pydantic import BaseModel, Field


class ValidationStatus(str, Enum):
    """验证状态枚举。"""
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"


class CheckResult(BaseModel):
    """单检查项结果。

    Attributes:
        name:     检查项名称，如 "llm_init"、"embedding_dim"。
        status:   验证状态。
        message:  消息（失败或跳过原因）。
        latency:  耗时（毫秒）。
        details:  扩展数据。
    """
    name: str
    status: ValidationStatus
    message: str = ""
    latency: float = 0.0
    details: dict[str, Any] = Field(default_factory=dict)


class ValidationReport(BaseModel):
    """验证报告。

    Attributes:
        status:     整体验证结果。
        module:     被验证的模块名称，如 ``"document"``。
        duration_ms: 验证耗时（毫秒）。
        message:    错误或提示消息。
        checks:     子检查项列表（V2 新增）。
        summary:    概要信息（V2 新增）。
        details:    详细结果字典。
    """
    status: str  # "success" | "failed"（兼容 V1；新增 ValidationStatus 见 checks）
    module: str
    duration_ms: float
    message: str | None = None
    checks: list[CheckResult] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)
    details: dict[str, Any] = Field(default_factory=dict)

    # ── V1 兼容工厂方法 ──────────────────────────

    @classmethod
    def ok(cls, module: str, **details: Any) -> "ValidationReport":
        """快速创建成功报告（V1 兼容）。"""
        return cls(
            status="success",
            module=module,
            duration_ms=0.0,
            details=details,
        )

    @classmethod
    def fail(cls, module: str, message: str, **details: Any) -> "ValidationReport":
        """快速创建失败报告（V1 兼容）。"""
        return cls(
            status="failed",
            module=module,
            duration_ms=0.0,
            message=message,
            details=details,
        )

    def complete(self, start: float) -> "ValidationReport":
        """验证结束后填入实际耗时并返回自身。"""
        self.duration_ms = round((time() - start) * 1000, 2)
        return self

    # ── V2 工厂方法 ──────────────────────────────

    @classmethod
    def from_checks(
        cls,
        module: str,
        checks: list[CheckResult],
        message: Optional[str] = None,
        **details: Any,
    ) -> "ValidationReport":
        """从子检查项列表构建报告。

        自动计算：
        - status（任一 FAIL 则整体 FAIL，全部 SKIP 则 SKIP）
        - summary（pass/fail/skip 计数）
        """
        pass_count = sum(1 for c in checks if c.status == ValidationStatus.PASS)
        fail_count = sum(1 for c in checks if c.status == ValidationStatus.FAIL)
        skip_count = sum(1 for c in checks if c.status == ValidationStatus.SKIP)

        if fail_count > 0:
            status = "failed"
        elif pass_count == 0:
            status = "failed"  # 全 SKIP 视为失败
            message = message or "所有检查项均被跳过"
        else:
            status = "success"

        return cls(
            status=status,
            module=module,
            duration_ms=0.0,
            message=message,
            checks=checks,
            summary={
                "total": len(checks),
                "pass": pass_count,
                "fail": fail_count,
                "skip": skip_count,
            },
            details=details,
        )


class ChatResult(BaseModel):
    """Chat 验证结果。

    Attributes:
        answer:           LLM 生成的答案。
        sources:          检索来源列表。
        retrieval_time:   检索耗时（ms）。
        generation_time:  生成耗时（ms）。
        total_time:       总耗时（ms）。
        metadata:         扩展元数据。
    """
    answer: str = ""
    sources: list[dict[str, Any]] = Field(default_factory=list)
    retrieval_time: float = 0.0
    generation_time: float = 0.0
    total_time: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class StatusResult(BaseModel):
    """系统状态快照。

    Attributes:
        core:       Core 模块状态。
        retrieval:  Retrieval 模块状态。
        generation: Generation 模块状态。
        details:    各组件详细状态。
    """
    core: str = "unknown"
    retrieval: str = "unknown"
    generation: str = "unknown"
    details: dict[str, Any] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════
# V2: Scenario & Debug Models
# ═══════════════════════════════════════════════════

class ScenarioResult(BaseModel):
    """场景验证结果。

    Attributes:
        name:     场景名称，如 "knowledge_base_ingest"。
        status:   验证状态。
        duration: 耗时（秒）。
        checks:   子检查项列表。
        details:  场景详细数据。
    """
    name: str
    status: ValidationStatus = ValidationStatus.SKIP
    duration: float = 0.0
    checks: list[CheckResult] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class DebugResult(BaseModel):
    """诊断结果。

    Attributes:
        query:       诊断查询。
        sections:    诊断分区（如 "retrieval" / "generation" / "context"）。
        latency_ms:  总耗时。
        details:     各区诊断数据。
    """
    query: str
    sections: list[str] = Field(default_factory=list)
    latency_ms: float = 0.0
    details: dict[str, Any] = Field(default_factory=dict)
