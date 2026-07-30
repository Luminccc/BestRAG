"""ProviderFactory — Provider 工厂。

职责：
1. 根据配置创建 Provider 实例
2. 管理 Provider 注册到 Registry
3. 提供便捷获取各类型 Provider 的方法
"""

from typing import Any, Dict, Optional

from core.logger import get_logger
from core.registry import get_registry
from core.provider.base import BaseProvider

logger = get_logger("bestrag.provider.factory")


class ProviderFactory:
    """Provider 工厂。

    用法::

        factory = ProviderFactory()
        sim_provider = factory.create_similarity("jaccard")
        factory.register("similarity", "jaccard", sim_provider)
    """

    def create(
        self,
        provider_type: str,
        name: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> BaseProvider:
        """创建 Provider 实例并注册到 Registry。

        Args:
            provider_type: Provider 类型（"embedding" / "similarity" / "reranker" / "llm"）。
            name: Provider 名称。
            params: 创建参数。

        Returns:
            Provider 实例。
        """
        registry = get_registry()
        provider_cls = registry.provider.get(provider_type)
        params = params or {}
        instance = provider_cls(**params)
        instance.name = name
        logger.info(f"Provider 创建: {provider_type}:{name}")
        return instance

    def create_similarity(
        self,
        name: str = "jaccard",
    ) -> BaseProvider:
        """创建相似度 Provider。"""
        from core.provider.similarity import (
            CosineSimilarityProvider,
            JaccardSimilarityProvider,
        )
        providers = {
            "jaccard": JaccardSimilarityProvider,
            "cosine": CosineSimilarityProvider,
        }
        cls = providers.get(name)
        if cls is None:
            raise ValueError(f"不支持的相似度 Provider: {name}，可选: {list(providers)}")
        instance = cls()
        instance.name = name
        return instance

    @staticmethod
    def register_provider(
        provider_type: str,
        name: str,
        provider_cls: type,
    ) -> None:
        """将 Provider 类注册到 Registry。

        Args:
            provider_type: Provider 类型 key。
            name: Provider 名称 key。
            provider_cls: Provider 类。
        """
        registry = get_registry()
        key = f"{provider_type}:{name}" if provider_type else name
        registry.strategy.register(key, provider_cls)
        logger.info(f"Provider 注册: {key}")
