"""ApplicationContext — 运行时对象容器。

持有整个应用生命周期的共享对象：
- config:         全局配置（CoreConfig）
- registry:       服务注册中心（ServiceRegistry）
- resource_manager: 重量级资源管理器（ResourceManager）
- workspace_manager: 工作空间管理器（WorkspaceManager）
- services:       Domain Service 字典

不负责：
- 对象创建（由 Bootstrap 负责）
- 生命周期管理（由 Application 负责）
- 业务逻辑
"""

from typing import Any, Optional

from core.config import CoreConfig
from core.registry import ServiceRegistry


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
        self.registry: Optional[ServiceRegistry] = None
        self.resource_manager: Any = None   # ResourceManager
        self.workspace_manager: Any = None  # WorkspaceManager
        self.services: dict[str, Any] = {}

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
