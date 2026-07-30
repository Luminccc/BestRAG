"""StrategyFactory — 策略工厂。

职责：
1. 根据配置创建策略实例
2. 从 RegistryCenter 获取策略类并实例化
3. 提供便捷创建各类型策略的方法
"""

from typing import Any, Dict, Optional, Type

from core.logger import get_logger
from core.registry import get_registry
from core.strategy.base import BaseStrategy

logger = get_logger("bestrag.strategy.factory")


class StrategyFactory:
    """策略工厂。

    用法::

        factory = StrategyFactory()
        chunk_strategy = factory.create_chunk("recursive")
        retriever = factory.create_retriever("vector")
    """

    def create(
        self,
        strategy_type: str,
        name: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> BaseStrategy:
        """创建任意类型的策略实例。

        Args:
            strategy_type: 策略类型（"chunk" / "retrieval" / "fusion"）。
            name: 策略名称（在 Registry 中注册的名称）。
            params: 实例化参数字典。

        Returns:
            策略实例。

        Raises:
            KeyError: 策略未在 Registry 中注册。
        """
        registry = get_registry()
        strategy_cls = registry.strategy.get(f"{strategy_type}:{name}")
        params = params or {}
        instance = strategy_cls(**params)
        logger.info(f"策略创建: {strategy_type}:{name}")
        return instance

    def create_chunk(
        self,
        name: str = "recursive",
        **params: Any,
    ) -> BaseStrategy:
        """创建 Chunk 策略。"""
        return self.create("chunk", name, params)

    def create_retrieval(
        self,
        name: str = "vector",
        **params: Any,
    ) -> BaseStrategy:
        """创建检索策略。"""
        return self.create("retrieval", name, params)

    def create_fusion(
        self,
        name: str = "rrf",
        **params: Any,
    ) -> BaseStrategy:
        """创建 Fusion 策略。"""
        return self.create("fusion", name, params)
