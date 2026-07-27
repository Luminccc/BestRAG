"""Application 兼容导出。

Application 类已迁移至 core.application.application。
本文件保留为兼容入口，新代码请使用::

    from core.application import bootstrap
    from core.application import Application
"""


def __getattr__(name):
    if name == "Application":
        from core.application.application import Application
        return Application
    if name == "bootstrap":
        from core.application.bootstrap import bootstrap
        return bootstrap
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["Application", "bootstrap"]
