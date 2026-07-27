"""Application — 应用生命周期管理。

流程::

    bootstrap()  →  Application(ctx)
                        ├── start()
                        │     ├── ResourceManager.init_all()
                        │     └── running = True
                        ├── stop()
                        │     ├── ResourceManager.close_all()
                        │     └── running = False

与 ApplicationContext 的关系：
    Application 持有 Context 引用，负责调用 ResourceManager 生命周期方法。
    Context 持有所有运行时对象。
"""

from core.application.context import ApplicationContext
from core.logger import get_logger

logger = get_logger("bestrag.application")


class Application:
    """BestRAG 应用入口。

    Usage::

        from core.application.bootstrap import bootstrap

        app = bootstrap()   # 组装完毕
        app.start()         # 初始化资源
        # ... 业务运行 ...
        app.stop()          # 释放资源
    """

    def __init__(self, context: ApplicationContext):
        self._ctx = context
        self._running = False

    # ── 生命周期 ──────────────────────────────────

    def start(self) -> None:
        """启动应用：初始化所有 Provider 资源。"""
        cfg = self._ctx.config
        app_cfg = cfg.app if cfg else None
        name = app_cfg.name if app_cfg else "BestRAG"
        version = app_cfg.version if app_cfg else "0.1.0"
        logger.info(f"{name} v{version} 启动中...")

        if self._ctx.resource_manager:
            self._ctx.resource_manager.init_all()

        self._running = True
        logger.info("应用就绪")

    def stop(self) -> None:
        """关闭应用：释放所有 Provider 资源。"""
        logger.info("应用关闭中...")

        if self._ctx.resource_manager:
            self._ctx.resource_manager.close_all()

        self._running = False
        logger.info("应用已关闭")

    # ── 属性 ──────────────────────────────────────

    @property
    def context(self) -> ApplicationContext:
        return self._ctx

    @property
    def is_running(self) -> bool:
        return self._running
