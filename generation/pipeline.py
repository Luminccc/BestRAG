"""GenerationPipeline — 生成管线编排。

流程::

    Context → Prompt → LLM → Answer

不负责检索（检索由调用方完成并传入 context）。
"""

from typing import List, Optional

from core.config import get_config
from core.logger import get_logger
from core.registry import ServiceRegistry
from generation.context.builder import ContextBuilder
from generation.exception import GenerationError
from generation.model import GenerationRequest, GenerationResponse
from generation.prompt.builder import PromptBuilder
from generation.provider.openai_compatible import OpenAICompatibleProvider

logger = get_logger(__name__)

_LLM_KEY = "llm"

# Registry key，与 retrieval/retriever/model.py 的 RetrievalResult 保持一致
from retrieval.retriever.model import RetrievalResult


class GenerationPipeline:
    """生成管线 — Context → Prompt → LLM → Answer。

    Usage::

        pipeline = GenerationPipeline()
        response = pipeline.generate("如何部署?", context="[Document 1]...")
    """

    def __init__(
        self,
        context_builder: Optional[ContextBuilder] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        llm_provider: Optional[OpenAICompatibleProvider] = None,
    ):
        self._context_builder = context_builder or ContextBuilder()
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._llm = llm_provider

    # ── 主入口 ────────────────────────────────────

    def generate(
        self,
        query: str,
        context: str = "",
        results: Optional[List[RetrievalResult]] = None,
        system_prompt: Optional[str] = None,
    ) -> GenerationResponse:
        """执行生成管线。

        Args:
            query:         用户问题。
            context:       预构建的上下文字符串（与 results 二选一，context 优先）。
            results:       检索结果列表（传入时自动调用 ContextBuilder）。
            system_prompt: 自定义 system prompt。

        Returns:
            GenerationResponse（answer / model / sources）。
        """
        try:
            # Step 1: 构建 Context（如果给了 results 而非 context）
            if not context and results:
                context = self._context_builder.build(results)

            # Step 2: 构建 Prompt
            messages = self._prompt_builder.build(query, context, system_prompt)

            # Step 3: 调用 LLM
            provider = self._get_llm()
            cfg = get_config().generation
            answer = provider.generate(messages)

            return GenerationResponse(
                answer=answer,
                model=cfg.model_name,
                sources=[{"content": context}] if context else [],
            )

        except GenerationError:
            raise
        except Exception as e:
            raise GenerationError(f"生成管线执行失败: {e}") from e

    # ── 内部 ──────────────────────────────────────

    def _get_llm(self):
        """从 Registry 获取 LLM Provider，未注册则创建默认实例。"""
        if self._llm:
            return self._llm
        try:
            return ServiceRegistry().get(_LLM_KEY)
        except Exception:
            # 未注册时创建默认 OpenAICompatibleProvider
            provider = OpenAICompatibleProvider()
            ServiceRegistry().register(_LLM_KEY, provider)
            return provider
