"""Registry 包 — 统一注册中心。

提供六大类注册表：
- ServiceRegistry   : 运行时服务
- StrategyRegistry  : 策略插件
- ProviderRegistry  : Provider（LLM/Embedding/VectorStore）
- EvaluatorRegistry : 评估器
- ModelRegistry     : v0.3 模型类
- RepositoryRegistry: v0.3 数据仓库

全局入口::

    from core.registry import get_registry
    rc = get_registry()
    rc.service.register("doc", DocumentService(...))
    rc.strategy.get("semantic")

v0.1 兼容接口仍然可用::

    from core.registry import get_service, register_service
"""

from typing import Any, Type, TypeVar

from core.registry.center import RegistryCenter, get_registry
from core.registry.service import ServiceRegistry
from core.registry.model import ModelRegistry
from core.registry.repository import RepositoryRegistry

T = TypeVar("T")

__all__ = [
    # 新 API
    "RegistryCenter",
    "get_registry",
    "ServiceRegistry",
    "ModelRegistry",
    "RepositoryRegistry",
    # 兼容 API
    "register_service",
    "register_service_factory",
    "get_service",
    "unregister_service",
    "clear_services",
]


# ═══════════════════════════════════════════════════
# v0.1 兼容函数 — 转发到 RegistryCenter.service
# ═══════════════════════════════════════════════════

def register_service(name: str, service: Any) -> None:
    """注册服务实例（兼容 v0.1 API）。"""
    get_registry().service.register(name, service)


def register_service_factory(name: str, factory: callable) -> None:
    """注册服务工厂（兼容 v0.1 API）。"""
    get_registry().service.register_factory(name, factory)


def get_service(name: str, service_type: Type[T] = Any) -> T:
    """获取服务实例（兼容 v0.1 API）。"""
    return get_registry().service.get(name, service_type)


def unregister_service(name: str) -> None:
    """注销服务（兼容 v0.1 API）。"""
    get_registry().service.remove(name)


def clear_services() -> None:
    """清空所有服务注册（兼容 v0.1 API）。"""
    get_registry().service.clear()
