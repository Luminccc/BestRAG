"""TransformerService — Transformer 编排服务。

独立调用入口，不绑定到 ProcessorService 管线。
使用方（API/CLI）决定何时调用 Transformer。
"""

from document.model import Document

from .base import BaseTransformer
from .schema_transformer import SchemaTransformer


class TransformerService:
    """Transformer 编排服务。

    Usage::

        service = TransformerService()
        normalized = service.transform(document)
    """

    def __init__(self, transformer: BaseTransformer | None = None):
        self._transformer = transformer or SchemaTransformer()

    def transform(self, document: Document) -> Document:
        """对 Document 执行标准化转换。

        Args:
            document: 输入 Document。

        Returns:
            标准化后的 Document。
        """
        return self._transformer.transform(document)
