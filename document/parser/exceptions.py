"""Parser 异常定义。

所有 Parser 相关异常统一放在此模块，方便上层捕获和处理。
"""


class ParserError(Exception):
    """解析过程中发生的通用错误。

    包括：文件格式不兼容、解析库异常、内容损坏等。
    文件不存在请使用内置 FileNotFoundError。
    """
    pass
