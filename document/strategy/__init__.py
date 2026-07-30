"""Parser Strategy — 文档解析策略层。

提供：
- BaseParserStrategy：解析策略基类
- MetadataExtractor：元数据提取器

用法::

    from document.strategy import BaseParserStrategy, MetadataExtractor
"""

from document.strategy.base import BaseParserStrategy
from document.strategy.metadata import MetadataExtractor

__all__ = [
    "BaseParserStrategy",
    "MetadataExtractor",
]
