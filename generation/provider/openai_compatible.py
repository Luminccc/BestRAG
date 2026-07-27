"""OpenAICompatibleProvider — OpenAI 兼容 API 的 LLM Provider。

通过 openai SDK 接入所有 OpenAI 兼容接口，包括：
OpenAI / DeepSeek / Qwen / Kimi / 智谱 / SiliconFlow / Ollama / vLLM

仅需配置 base_url + api_key + model 即可切换，无需修改代码。
"""

from typing import Any, Dict, List

from core.config import get_config
from core.logger import get_logger

from .base import BaseLLMProvider

logger = get_logger(__name__)


class OpenAICompatibleProvider(BaseLLMProvider):
    """OpenAI 兼容 API Provider。

    Usage::

        provider = OpenAICompatibleProvider()
        answer = provider.generate([
            {"role": "system", "content": "你是企业知识助手"},
            {"role": "user", "content": "如何部署RAG？"},
        ])
    """

    def __init__(self):
        cfg = get_config().generation
        self._model = cfg.model_name
        self._temperature = cfg.temperature
        self._base_url = cfg.base_url
        self._api_key = cfg.api_key

    # ── 公开接口 ──────────────────────────────────

    def generate(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """调用 LLM 生成回答。

        Args:
            messages: OpenAI 格式消息列表。
            **kwargs: 覆盖默认 temperature / max_tokens。

        Returns:
            生成的文本内容。
        """
        from openai import OpenAI

        temperature = kwargs.get("temperature", self._temperature)

        client = OpenAI(base_url=self._base_url, api_key=self._api_key or None)

        try:
            response = client.chat.completions.create(
                model=self._model,
                messages=messages,  # type: ignore
                temperature=temperature,
            )
            content = response.choices[0].message.content or ""
            logger.info(f"LLM 生成完成: model={self._model}, len={len(content)}")
            return content
        except Exception as e:
            from generation.exception import ProviderError
            raise ProviderError(f"LLM 调用失败: {e}") from e
