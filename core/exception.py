"""异常处理模块 — 提供统一的异常定义和处理能力。

定义：
- 基础异常类
- 各模块特定异常
"""

from typing import Optional


class BestRAGException(Exception):
    """BestRAG 基础异常类。"""

    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ConfigException(BestRAGException):
    """配置异常。"""
    pass


class ServiceNotFoundException(BestRAGException):
    """服务未找到异常。"""
    pass


class EmbeddingException(BestRAGException):
    """Embedding 异常。"""
    pass


class VectorStoreException(BestRAGException):
    """向量存储异常。"""
    pass


class RetrievalException(BestRAGException):
    """检索异常。"""
    pass


class RerankException(BestRAGException):
    """重排序异常。"""
    pass