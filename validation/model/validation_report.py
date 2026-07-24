"""ValidationReport — 验证结果统一数据协议。

所有 validation check 统一使用此模型输出。
使用 Pydantic v2 确保序列化和类型安全。
"""

from time import time
from typing import Any

from pydantic import BaseModel, Field


class ValidationReport(BaseModel):
    """验证报告。

    Attributes:
        status:     验证结果，``"success"`` 或 ``"failed"``。
        module:     被验证的模块名称，如 ``"document"``。
        duration_ms: 验证耗时（毫秒）。
        message:    错误或提示消息，成功时可为空。
        details:    详细结果字典，存放各检查项的输出。
    """
    status: str  # "success" | "failed"
    module: str
    duration_ms: float
    message: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def ok(cls, module: str, **details: Any) -> "ValidationReport":
        """快速创建成功报告。"""
        return cls(
            status="success",
            module=module,
            duration_ms=0.0,
            details=details,
        )

    @classmethod
    def fail(cls, module: str, message: str, **details: Any) -> "ValidationReport":
        """快速创建失败报告。"""
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
