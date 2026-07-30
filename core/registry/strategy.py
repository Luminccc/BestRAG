"""StrategyRegistry — 策略插件注册表。

管理各种策略类（Chunk / Retriever / Fusion 等）的注册与发现。
策略以 class（而非实例）注册，由工厂按需创建。
"""

from typing import Any, Dict, Type

from core.registry.base import BaseRegistry


class StrategyRegistry(BaseRegistry):
    """策略注册表，存储策略 class。"""

    def __init__(self):
        self._strategies: Dict[str, Type[Any]] = {}

    def register(self, name: str, strategy_cls: Type[Any]) -> None:
        """注册策略类。

        Args:
            name: 策略名称（如 "semantic"、"recursive"）。
            strategy_cls: 策略类（必须可实例化）。
        """
        self._strategies[name] = strategy_cls

    def get(self, name: str) -> Type[Any]:
        """获取已注册的策略类。

        Raises:
            KeyError: 策略未注册。
        """
        if name not in self._strategies:
            raise KeyError(f"Strategy '{name}' not found, available: {list(self._strategies)}")
        return self._strategies[name]

    def has(self, name: str) -> bool:
        """检查策略是否已注册。"""
        return name in self._strategies

    def remove(self, name: str) -> None:
        """移除指定策略。"""
        self._strategies.pop(name, None)

    def clear(self) -> None:
        """清空所有策略注册。"""
        self._strategies.clear()

    def list(self) -> list[str]:
        """列出所有已注册的策略名。"""
        return list(self._strategies.keys())
