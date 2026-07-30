"""GenerationTrace — 生成 Trace 接口（v0.3 Phase 2 预留）。

记录 LLM 生成过程的 Trace 数据：
- prompt
- response
- token usage
- latency
"""

from typing import Any, Dict, Optional

from core.logger import get_logger
from core.models.trace import SpanStatus, TraceStatus, TraceType
from trace.context import TraceContext

logger = get_logger("trace.generation")


class GenerationTrace:
    """生成 Trace 助手。

    记录 LLM 调用过程的完整 Trace。
    Phase 5 Generation Layer 将基于此构建。
    """

    @staticmethod
    def record_prompt(ctx: TraceContext, prompt: str, system_prompt: str = "") -> None:
        """记录 Prompt 信息。"""
        ctx.record_event("prompt_built", {
            "prompt_length": len(prompt),
            "system_prompt_length": len(system_prompt),
        })

    @staticmethod
    def record_response(ctx: TraceContext, response: str, model: str) -> None:
        """记录 LLM 响应。"""
        ctx.record_event("response_received", {
            "response_length": len(response),
            "model": model,
        })

    @staticmethod
    def record_usage(
        ctx: TraceContext,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
    ) -> None:
        """记录 Token 使用量。"""
        ctx.record_metric("prompt_tokens", prompt_tokens)
        ctx.record_metric("completion_tokens", completion_tokens)
        ctx.record_metric("total_tokens", total_tokens)

    @staticmethod
    def start_generation_trace(
        ctx: TraceContext,
        query: str,
        model: str,
    ) -> None:
        """开始一次生成 Trace。"""
        ctx.start_trace(
            TraceType.GENERATION,
            metadata={"query": query, "model": model},
        )

    @staticmethod
    def end_generation_trace(ctx: TraceContext, failed: bool = False) -> None:
        """结束生成 Trace。"""
        ctx.end_trace(TraceStatus.FAILED if failed else TraceStatus.SUCCESS)
