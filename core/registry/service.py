"""ServiceRegistry — 运行时服务注册表。

负责管理 Domain Service 实例，支持：
- 实例注册
- 工厂函数延迟创建（首次 get 时懒加载并缓存）
- 兼容 v0.1 API
"""

from typing import Any, Dict, Type, TypeVar

from core.exception import ServiceNotFoundError
from core.registry.base import BaseRegistry

T = TypeVar("T")


class ServiceRegistry(BaseRegistry):
    """服务注册表（非单例 — 由 RegistryCenter 统一管理）。"""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}  # type: ignore

    # ── 注册 ──────────────────────────────────────

    def register(self, name: str, service: Any) -> None:
        """注册服务实例（覆盖同名 factory）。"""
        self._services[name] = service
        self._factories.pop(name, None)

    def register_factory(self, name: str, factory: callable) -> None:
        """注册服务工厂函数（get 时懒加载）。"""
        self._factories[name] = factory
        self._services.pop(name, None)

    # ── 获取 ──────────────────────────────────────

    def get(self, name: str, service_type: Type[T] = Any) -> T:
        """获取服务实例。

        优先返回已注册实例；无实例则尝试调用工厂创建并缓存。
        """
        if name in self._services:
            return self._services[name]

        if name in self._factories:
            service = self._factories[name]()
            self._services[name] = service
            del self._factories[name]
            return service

        raise ServiceNotFoundError(f"Service '{name}' not found")

    def has(self, name: str) -> bool:
        """检查服务是否已注册（含工厂）。"""
        return name in self._services or name in self._factories

    # ── 移除（BaseRegistry 接口） ────────────────

    def remove(self, name: str) -> None:
        """移除指定服务（BaseRegistry 接口）。"""
        self._services.pop(name, None)
        self._factories.pop(name, None)

    def unregister(self, name: str) -> None:
        """注销服务（v0.1 兼容名称）。"""
        self.remove(name)

    # ── 清空 ──────────────────────────────────────

    def clear(self) -> None:
        """清空所有注册（主要用于 shutdown）。"""
        self._services.clear()
        self._factories.clear()

    def list(self) -> list[str]:
        """列出所有已注册的服务名。"""
        return list(self._services.keys()) + list(self._factories.keys())
