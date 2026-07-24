"""BaseCleaner — Cleaner 抽象基类。

所有 Cleaner 必须实现此接口，接收 Document 返回 Document。
Cleaner 只负责文本规范化，不负责切分、嵌入、元数据增强。
"""

from abc import ABC, abstractmethod

from document.model import Document


class BaseCleaner(ABC):
    """Cleaner 抽象契约。

    所有文本清洗器（TextCleaner、HTMLCleaner 等）必须实现此接口。
    """

    @abstractmethod
    def clean(self, document: Document) -> Document:
        """对 Document.content 执行清洗处理。

        Args:
            document: 待清洗的 Document 对象。

        Returns:
            清洗后的 Document 对象（同一模型的干净实例）。
        """
        ...
