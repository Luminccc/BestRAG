"""EvaluatorRegistry — 评估器注册表。

管理 RecallEvaluator、AccuracyEvaluator、FaithfulnessEvaluator 等评估器类。
评估器以 class 注册，由 Evaluation Runner 按需创建。
"""

from typing import Any, Dict, Type

from core.registry.base import BaseRegistry


class EvaluatorRegistry(BaseRegistry):
    """评估器注册表。"""

    def __init__(self):
        self._evaluators: Dict[str, Type[Any]] = {}

    def register(self, name: str, evaluator_cls: Type[Any]) -> None:
        """注册评估器类。

        Args:
            name: 评估器名称（如 "recall"、"accuracy"）。
            evaluator_cls: 评估器类。
        """
        self._evaluators[name] = evaluator_cls

    def get(self, name: str) -> Type[Any]:
        """获取已注册的评估器类。

        Raises:
            KeyError: 评估器未注册。
        """
        if name not in self._evaluators:
            raise KeyError(f"Evaluator '{name}' not found, available: {list(self._evaluators)}")
        return self._evaluators[name]

    def has(self, name: str) -> bool:
        """检查评估器是否已注册。"""
        return name in self._evaluators

    def remove(self, name: str) -> None:
        """移除指定评估器。"""
        self._evaluators.pop(name, None)

    def clear(self) -> None:
        """清空所有评估器注册。"""
        self._evaluators.clear()

    def list(self) -> list[str]:
        """列出所有已注册的评估器名称。"""
        return list(self._evaluators.keys())
