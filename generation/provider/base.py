"""BaseLLMProvider — LLM Provider 抽象契约。

所有 LLM Provider 必须实现此接口。
V1 只支持 generate()；stream_generate() 为 V2 预留。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseLLMProvider(ABC):
    """LLM Provider 抽象基类。"""

    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """同步生成回答。

        Args:
            messages: OpenAI 格式的消息列表 [{"role":"system","content":"..."}, ...]。
            **kwargs: 额外参数（temperature / max_tokens 等）。

        Returns:
            LLM 生成的文本回答。
        """
        ...

    def stream_generate(self, messages: List[Dict[str, str]], **kwargs: Any):
        """流式生成（V2 预留，V1 默认 fallback 到 generate()）。"""
        yield self.generate(messages, **kwargs)
