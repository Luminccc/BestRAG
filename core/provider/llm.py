"""BaseLLMProvider — LLM Provider 抽象。

负责与大语言模型交互，生成回答。

实现（未来）：
- OpenAILLMProvider
- DeepSeekLLMProvider
- LocalLLMProvider
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional

from core.provider.base import BaseProvider


class BaseLLMProvider(BaseProvider):
    """LLM Provider 基类。"""

    name: str = "base_llm"

    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> str:
        """生成回答。

        Args:
            messages: 对话消息列表。
            temperature: 生成温度。
            max_tokens: 最大输出 token。
            **kwargs: 其他模型参数。

        Returns:
            生成的文本。
        """

    def execute(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """委托给 generate。"""
        return self.generate(messages, **kwargs)
