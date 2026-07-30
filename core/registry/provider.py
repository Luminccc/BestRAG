"""ProviderRegistry — Provider 注册表。

管理 EmbeddingProvider、LLMProvider、VectorStoreProvider 等实例。
"""

from typing import Any, Dict

from core.registry.base import BaseRegistry


class ProviderRegistry(BaseRegistry):
    """Provider 注册表。"""

    def __init__(self):
        self._providers: Dict[str, Any] = {}

    def register(self, name: str, provider: Any) -> None:
        """注册 Provider 实例。

        Args:
            name: Provider 类型名称（如 "embedding"、"llm"、"vectorstore"）。
            provider: Provider 实例。
        """
        self._providers[name] = provider

    def get(self, name: str) -> Any:
        """获取已注册的 Provider 实例。

        Raises:
            KeyError: Provider 未注册。
        """
        if name not in self._providers:
            raise KeyError(f"Provider '{name}' not found, available: {list(self._providers)}")
        return self._providers[name]

    def has(self, name: str) -> bool:
        """检查 Provider 是否已注册。"""
        return name in self._providers

    def remove(self, name: str) -> None:
        """移除指定 Provider。"""
        self._providers.pop(name, None)

    def clear(self) -> None:
        """清空所有 Provider 注册。"""
        self._providers.clear()

    def list(self) -> list[str]:
        """列出所有已注册的 Provider 名称。"""
        return list(self._providers.keys())
