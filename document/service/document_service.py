"""DocumentService — Document 流程编排层。

职责：串联 Dispatcher → Parser 完成文件到 Document 的转换。
不负责：文件解析、Parser 选择、清洗、切片等具体实现。
"""

from document.dispatcher import DocumentDispatcher
from document.model import Document


class DocumentService:
    """文档服务 — 对外提供的 Document 创建入口。

    Usage::

        dispatcher = DocumentDispatcher()
        service = DocumentService(dispatcher)
        doc = service.create_document("/data/report.pdf")
    """

    def __init__(self, dispatcher: DocumentDispatcher):
        self._dispatcher = dispatcher

    def create_document(self, file_path: str) -> Document:
        """将指定文件解析为 Document 对象。

        编排链路：
            Dispatcher.dispatch() → Parser.parse() → Document

        Args:
            file_path: 待解析文件的路径。

        Returns:
            包含提取内容和基础元数据的 Document 对象。

        Raises:
            FileNotFoundError:          文件不存在。
            UnsupportedFileTypeError:   文件类型无对应 Parser。
            ParserError:                Parser 解析过程中出错。
        """
        return self._dispatcher.dispatch(file_path)
