"""日志模块 — 提供统一的日志记录能力。

支持：
- 不同级别的日志记录
- 结构化日志
- 日志文件输出
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class Logger:
    """日志记录器。"""

    def __init__(self, name: str = "bestrag", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # 避免重复添加处理器
        if not self.logger.handlers:
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

            # 文件处理器
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / f"bestrag_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str, **kwargs: Any) -> None:
        """记录调试日志。"""
        if kwargs:
            message = f"{message} | {kwargs}"
        self.logger.debug(message)

    def info(self, message: str, **kwargs: Any) -> None:
        """记录信息日志。"""
        if kwargs:
            message = f"{message} | {kwargs}"
        self.logger.info(message)

    def warning(self, message: str, **kwargs: Any) -> None:
        """记录警告日志。"""
        if kwargs:
            message = f"{message} | {kwargs}"
        self.logger.warning(message)

    def error(self, message: str, **kwargs: Any) -> None:
        """记录错误日志。"""
        if kwargs:
            message = f"{message} | {kwargs}"
        self.logger.error(message)

    def critical(self, message: str, **kwargs: Any) -> None:
        """记录严重错误日志。"""
        if kwargs:
            message = f"{message} | {kwargs}"
        self.logger.critical(message)


# 全局日志记录器实例
_default_logger: Optional[Logger] = None


def get_logger(name: str = "bestrag") -> Logger:
    """获取全局日志记录器实例。"""
    global _default_logger
    if _default_logger is None:
        _default_logger = Logger(name)
    return _default_logger