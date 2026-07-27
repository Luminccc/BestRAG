"""服务注册中心 — 统一服务注册和发现。

支持：
- 普通服务注册/获取
- 工厂函数延迟创建（首次 get 时懒加载并缓存）
- 移除/清空
"""

from typing import Any, Dict, Optional, Type, TypeVar

from core.exception import ServiceNotFoundError

T = TypeVar("T")


class ServiceRegistry:
    """服务注册中心（单例）。"""

    _instance: Optional["ServiceRegistry"] = None
    _services: Dict[str, Any] = {}
    _factories: Dict[str, callable] = {}  # type: ignore

    def __new__(cls) -> "ServiceRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

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

    # ── 移除 ──────────────────────────────────────

    def unregister(self, name: str) -> None:
        """注销服务。"""
        self._services.pop(name, None)
        self._factories.pop(name, None)

    def clear(self) -> None:
        """清空所有注册（主要用于 shutdown）。"""
        self._services.clear()
        self._factories.clear()


# ═══════════════════════════════════════════════════
# 全局入口
# ═══════════════════════════════════════════════════

_registry = ServiceRegistry()


def register_service(name: str, service: Any) -> None:
    """注册服务实例。"""
    _registry.register(name, service)


def register_service_factory(name: str, factory: callable) -> None:
    """注册服务工厂。"""
    _registry.register_factory(name, factory)


def get_service(name: str, service_type: Type[T] = Any) -> T:
    """获取服务实例。"""
    return _registry.get(name, service_type)


def unregister_service(name: str) -> None:
    """注销服务。"""
    _registry.unregister(name)


def clear_services() -> None:
    """清空所有服务注册。"""
    _registry.clear()
