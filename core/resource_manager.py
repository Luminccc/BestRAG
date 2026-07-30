"""ResourceManager — 重量级资源生命周期管理。

建立在 Registry 之上，负责：
- 模型（Embedding / Reranker）只初始化一次
- 多模块共享实例
- 统一释放资源

所有模块通过 Registry 获取资源，不做重复加载。
"""

from typing import Any, Dict, List

from core.exception import ResourceError
from core.logger import get_logger
from core.provider import BaseProvider
from core.registry import get_registry

logger = get_logger("bestrag.resource")


class ResourceManager:
    """重量级资源管理器。

    Usage::

        rm = ResourceManager()
        rm.init_all()          # 启动时初始化所有已注册资源
        rm.close_all()         # 关闭时释放所有资源
    """

    # ── 初始化 / 释放 ─────────────────────────────

    def init_all(self) -> None:
        """初始化所有已注册的 Provider 资源。"""
        rc = get_registry()
        svc_registry = rc.service
        services = list(svc_registry._services.keys())
        for name in services:
            svc = svc_registry._services.get(name)
            if isinstance(svc, BaseProvider):
                try:
                    logger.info(f"初始化资源: {name}")
                    svc.initialize()
                except Exception as e:
                    raise ResourceError(f"初始化资源 '{name}' 失败: {e}") from e

        # factories 信息日志（仅提示）
        factories = list(svc_registry._factories.keys())
        for name in factories:
            logger.info(f"延迟资源注册（将在首次 get 时初始化）: {name}")

    def close_all(self) -> None:
        """关闭所有已注册的 Provider 资源。"""
        rc = get_registry()
        svc_registry = rc.service

        # 先收集后关闭，避免遍历时修改 dict
        providers: List[tuple] = []
        for name, svc in svc_registry._services.items():
            if isinstance(svc, BaseProvider):
                providers.append((name, svc))

        for name, p in providers:
            try:
                logger.info(f"关闭资源: {name}")
                p.close()
            except Exception as e:
                logger.error(f"关闭资源 '{name}' 时出错: {e}")

        rc.clear_all()
