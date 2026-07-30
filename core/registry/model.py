"""ModelRegistry — 模型类注册表。

管理 BaseModel 子类的注册与发现，
用于 Runtime 根据名称动态创建 Model 实例。
"""

from typing import Any, Dict, Type

from core.registry.base import BaseRegistry


class ModelRegistry(BaseRegistry):
    """模型注册表，存储 Model 类。"""

    def __init__(self):
        self._models: Dict[str, Type[Any]] = {}

    def register(self, name: str, model_cls: Type[Any]) -> None:
        """注册 Model 类。"""
        self._models[name] = model_cls

    def get(self, name: str) -> Type[Any]:
        """获取已注册的 Model 类。"""
        if name not in self._models:
            raise KeyError(f"Model '{name}' 未注册，可用: {list(self._models)}")
        return self._models[name]

    def has(self, name: str) -> bool:
        """检查 Model 是否已注册。"""
        return name in self._models

    def remove(self, name: str) -> None:
        """移除指定 Model。"""
        self._models.pop(name, None)

    def clear(self) -> None:
        """清空所有 Model 注册。"""
        self._models.clear()

    def list(self) -> list[str]:
        """列出所有已注册的 Model 名称。"""
        return list(self._models.keys())
