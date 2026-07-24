"""服务注册中心 — 提供统一的服务注册和发现能力。

支持：
- 服务注册
- 服务发现
- 依赖注入
"""

from typing import Any, Dict, Type, TypeVar

T = TypeVar('T')


class ServiceRegistry:
    """服务注册中心。"""

    _instance: 'ServiceRegistry' = None  # type: ignore
    _services: Dict[str, Any] = {}
    _factories: Dict[str, callable] = {}  # type: ignore

    def __new__(cls) -> 'ServiceRegistry':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, name: str, service: Any) -> None:
        """注册服务实例。"""
        self._services[name] = service
        # 如果存在对应的工厂函数，移除它
        if name in self._factories:
            del self._factories[name]

    def register_factory(self, name: str, factory: callable) -> None:
        """注册服务工厂函数。"""
        self._factories[name] = factory
        # 如果存在对应的实例，移除它
        if name in self._services:
            del self._services[name]

    def get(self, name: str, service_type: Type[T]) -> T:
        """获取服务实例。"""
        # 如果已经有实例，直接返回
        if name in self._services:
            return self._services[name]

        # 如果有工厂函数，创建实例并缓存
        if name in self._factories:
            service = self._factories[name]()
            self._services[name] = service
            # 移除工厂函数以避免重复创建
            del self._factories[name]
            return service

        raise ValueError(f"Service '{name}' not found")

    def unregister(self, name: str) -> None:
        """注销服务。"""
        if name in self._services:
            del self._services[name]
        if name in self._factories:
            del self._factories[name]


# 全局服务注册中心实例
_service_registry = ServiceRegistry()


def register_service(name: str, service: Any) -> None:
    """注册服务实例。"""
    _service_registry.register(name, service)


def register_service_factory(name: str, factory: callable) -> None:
    """注册服务工厂函数。"""
    _service_registry.register_factory(name, factory)


def get_service(name: str, service_type: Type[T]) -> T:
    """获取服务实例。"""
    return _service_registry.get(name, service_type)


def unregister_service(name: str) -> None:
    """注销服务。"""
    _service_registry.unregister(name)