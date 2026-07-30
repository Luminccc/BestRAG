"""BaseParserStrategy — Parser 策略基类。

所有文档格式解析器（PDF/Markdown/Office/HTML）必须实现 parse 方法。
继承自 core.strategy.BaseStrategy，可注册到 StrategyRegistry。

execute 委托给 parse，保持与 BaseStrategy 兼容。
"""

from abc import abstractmethod
from typing import Any

from core.strategy.base import BaseStrategy
from document.model import ParsedDocument


class BaseParserStrategy(BaseStrategy):
    """Parser 策略基类。"""

    name: str = "base_parser"

    @abstractmethod
    def parse(self, file_path: str) -> ParsedDocument:
        """将文件解析为标准化 ParsedDocument。

        Args:
            file_path: 待解析文件的绝对或相对路径。

        Returns:
            包含结构化内容和元数据的 ParsedDocument。
        """

    def execute(self, file_path: str) -> ParsedDocument:
        """委托给 parse。"""
        return self.parse(file_path)
