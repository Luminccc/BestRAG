"""Generation Debug — 生成诊断工具。

用于 Debug：LLM 回答质量相关诊断。

输出：
- Context 内容（检索到的文档片段）
- Prompt 结构（System + User）
- LLM 调用信息（Model / Latency / Token 估算）
- 生成结果

不负责：
- 修改 Prompt
- 自动优化
"""

from time import time
from typing import Optional

from validation.model import DebugResult


def debug_generation(
    query: str,
    generation_service=None,
    retrieval_service=None,
    rerank_service=None,
    top_k: int = 5,
) -> DebugResult:
    """诊断生成流程，返回各阶段详情。

    流程：
        1. 执行检索获取 context
        2. 执行 Rerank（可选）
        3. 调用 Generation 生成回答
        4. 收集各环节数据

    Args:
        query:               查询文本。
        generation_service:  GenerationService 实例。
        retrieval_service:   RetrievalService 实例。
        rerank_service:      RerankService 实例。
        top_k:               检索数量。

    Returns:
        DebugResult（含各阶段诊断数据）。
    """
    sections: list[str] = []
    details: dict = {}
    total_start = time()

    if generation_service is None:
        return DebugResult(
            query=query,
            sections=["error"],
            details={"error": "GenerationService 未注入"},
        )

    try:
        # ── 1. Context 获取 ──
        context: str = ""
        if retrieval_service is not None:
            t1 = time()
            results = retrieval_service.retrieve(query, top_k=top_k)
            ret_latency = round((time() - t1) * 1000, 2)

            if rerank_service is not None and len(results) > 1:
                try:
                    results = rerank_service.rerank(query, results)
                except Exception:
                    pass

            context_chunks = [r.content for r in results[:top_k]]
            context = "\n".join(context_chunks)
            sections.append("context")
            details["context"] = {
                "chunk_count": len(results),
                "total_chars": len(context),
                "latency_ms": ret_latency,
                "preview": context[:500],
            }

        # ── 2. Prompt 检查 ──
        try:
            from generation.prompt.builder import PromptBuilder
            pb = PromptBuilder()
            from core.config import get_config
            cfg = get_config().generation

            # 模拟 PromptBuilder 产出的结构
            sections.append("prompt")
            details["prompt"] = {
                "system_prompt": cfg.system_prompt or "(内置默认)",
                "query": query,
                "context_length": len(context),
                "estimated_total_chars": len(query) + len(context) + 200,
            }
        except Exception as e:
            details["prompt"] = {"error": str(e)}

        # ── 3. LLM 调用 ──
        t2 = time()
        try:
            response = generation_service.generate(
                query=query,
                context=context,
            )
            gen_latency = round((time() - t2) * 1000, 2)
            sections.append("generation")
            details["generation"] = {
                "model": response.model if hasattr(response, "model") else "unknown",
                "answer_length": len(response.answer),
                "latency_ms": gen_latency,
                "answer_preview": response.answer[:300],
                "estimated_tokens": len(response.answer) // 2,  # 粗略估算
            }
        except Exception as e:
            details["generation"] = {"error": f"{type(e).__name__}: {e}"}

    except Exception as e:
        details["error"] = f"{type(e).__name__}: {e}"
        sections.append("error")

    return DebugResult(
        query=query,
        sections=sections,
        latency_ms=round((time() - total_start) * 1000, 2),
        details=details,
    )
