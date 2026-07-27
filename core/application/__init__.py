"""Application Container — 运行时管理层。

提供：
- ApplicationContext: 运行时对象容器
- Application:        应用生命周期管理
- bootstrap:          应用组装入口
"""

from core.application.application import Application
from core.application.context import ApplicationContext
from core.application.bootstrap import bootstrap

__all__ = [
    "Application",
    "ApplicationContext",
    "bootstrap",
]
