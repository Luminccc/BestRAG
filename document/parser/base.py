"""BaseParser — 所有 Parser 的统一抽象基类。

每个 Parser 接收一个文件路径，返回统一的 Document 对象。
Parser 只负责格式转换，不负责清洗、切片、嵌入等操作。
"""

from abc import ABC, abstractmethod

from document.model import Document


class BaseParser(ABC):
    """Parser 抽象契约。

    所有文档格式（PDF / DOCX / Markdown / TXT 等）必须实现此接口。
    """

    @abstractmethod
    def parse(self, file_path: str) -> Document:
        """将指定文件解析为 Document 对象。

        Args:
            file_path: 待解析文件的绝对或相对路径。

        Returns:
            包含提取内容和基础元数据的 Document 对象。

        Raises:
            FileNotFoundError: 文件不存在。
            ParserError: 解析过程中发生错误。
        """
        ...
