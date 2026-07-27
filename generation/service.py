"""GenerationService — 生成服务入口。

对外提供 generate() 接口，通过 Registry 获取 LLM Provider。
"""

from typing import List, Optional

from core.logger import get_logger
from core.registry import get_service, register_service_factory
from generation.exception import GenerationError
from generation.model import GenerationResponse
from generation.pipeline import GenerationPipeline
from retrieval.retriever.model import RetrievalResult

logger = get_logger(__name__)


class GenerationService:
    """生成服务 — 提供统一生成入口。

    Usage::

        svc = GenerationService()
        response = svc.generate("如何部署?", results=retrieval_results)
    """

    def __init__(self, pipeline: Optional[GenerationPipeline] = None):
        self._pipeline = pipeline or GenerationPipeline()

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
            context:       预构建上下文字符串。
            results:       检索结果列表（与 context 二选一）。
            system_prompt: 自定义 system prompt。

        Returns:
            GenerationResponse。
        """
        logger.info(f"生成开始: {query[:50]}...")
        response = self._pipeline.generate(
            query=query,
            context=context,
            results=results,
            system_prompt=system_prompt,
        )
        logger.info(f"生成完成: model={response.model}, len={len(response.answer)}")
        return response


# ── Registry 注册 ──────────────────────────────

def _create_generation_service() -> GenerationService:
    return GenerationService()


register_service_factory("generation", _create_generation_service)


def get_generation_service() -> GenerationService:
    """获取 GenerationService 实例。"""
    return get_service("generation", GenerationService)
