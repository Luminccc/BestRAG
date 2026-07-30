"""ApplicationContext — 运行时对象容器。

持有整个应用生命周期的共享对象：
- config:         全局配置（CoreConfig）
- registry:       注册中心（RegistryCenter）
- resource_manager: 重量级资源管理器（ResourceManager）
- workspace_manager: 工作空间管理器（WorkspaceManager）
- services:       Domain Service 字典
- models:         v0.3 Model 实例字典
- repositories:   v0.3 Repository 实例字典

不负责：
- 对象创建（由 Bootstrap 负责）
- 生命周期管理（由 Application 负责）
- 业务逻辑
"""

from typing import Any, Dict, Optional

from core.config import CoreConfig
from core.registry.center import RegistryCenter


class ApplicationContext:
    """运行时上下文，保存所有共享对象引用。

    Usage::

        ctx = ApplicationContext()
        ctx.config = get_config()
        ctx.services["document"] = DocumentService(...)
        # ...
        doc_svc = ctx.get_service("document")
    """

    def __init__(self):
        self.config: Optional[CoreConfig] = None
        self.registry: Optional[RegistryCenter] = None
        self.resource_manager: Any = None   # ResourceManager
        self.workspace_manager: Any = None  # WorkspaceManager
        self.services: dict[str, Any] = {}

        # v0.3 扩展
        self.models: dict[str, Any] = {}
        self.repositories: dict[str, Any] = {}

    # ── Service 访问 ──────────────────────────────

    def get_service(self, name: str) -> Any:
        """获取已注册的 Domain Service。

        Raises:
            KeyError: 服务未注册。
        """
        if name not in self.services:
            raise KeyError(f"Service '{name}' 未注册，可用: {list(self.services.keys())}")
        return self.services[name]

    def has_service(self, name: str) -> bool:
        """检查服务是否已注册。"""
        return name in self.services

    # ── Model 访问（v0.3） ────────────────────────

    def get_model(self, name: str) -> Any:
        """获取已注册的 Model 实例。"""
        if name not in self.models:
            raise KeyError(f"Model '{name}' 未注册，可用: {list(self.models.keys())}")
        return self.models[name]

    # ── Repository 访问（v0.3） ───────────────────

    def get_repository(self, name: str) -> Any:
        """获取已注册的 Repository 实例。"""
        if name not in self.repositories:
            raise KeyError(f"Repository '{name}' 未注册，可用: {list(self.repositories.keys())}")
        return self.repositories[name]
