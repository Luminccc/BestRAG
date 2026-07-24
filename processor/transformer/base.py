"""BaseTransformer — Transformer 抽象基类。

每个 Transformer 接收 Document 返回 Document，
只做数据标准化，不做内容生成（摘要、关键词等 AI 增强）。
"""

from abc import ABC, abstractmethod

from document.model import Document


class BaseTransformer(ABC):
    """Transformer 抽象契约。

    所有数据转换器（SchemaTransformer 等）必须实现此接口。
    """

    @abstractmethod
    def transform(self, document: Document) -> Document:
        """对 Document 执行标准化转换。

        Args:
            document: 输入 Document（可来自 Cleaner 或 ChunkService 之后）。

        Returns:
            标准化后的 Document。
        """
        ...
