"""Dispatcher 异常定义。

涵盖文件类型不支持、Parser 未注册等调度层特有的错误场景。
"""


class UnsupportedFileTypeError(Exception):
    """文件类型不支持。

    场景：
        上传 .exe / .dll / 其他无对应 Parser 的文件格式时抛出。
    """
    pass


class ParserNotFoundError(Exception):
    """文件类型对应的 Parser 未在 Registry 中注册。

    场景：
        文件类型已知（如 xlsx），但尚未有 Parser 实现。
    """
    pass
