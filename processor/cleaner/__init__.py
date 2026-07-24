"""Processor Cleaner — 文本规范化清洗层。

所有 Cleaner 遵循 BaseCleaner 接口，接收 Document 返回 Document。
"""

from .base import BaseCleaner
from .text_cleaner import TextCleaner

__all__ = [
    "BaseCleaner",
    "TextCleaner",
]
