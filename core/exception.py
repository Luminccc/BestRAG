"""异常处理模块 — 统一异常定义。

层次结构：:

    BestRAGException（根）
        ├── ConfigError
        ├── ProviderError
        ├── ResourceError
        ├── CoreRuntimeError
        ├── ServiceNotFoundError
        ├── EmbeddingException
        ├── VectorStoreException
        ├── RetrievalException
        └── RerankException
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


# ── PDR Core 异常层次 ──────────────────────────────

class ConfigError(BestRAGException):
    """配置相关错误（读取失败、缺失必填项、格式错误）。"""
    pass


class ProviderError(BestRAGException):
    """Provider 初始化/运行/关闭过程中的错误。"""
    pass


class ResourceError(BestRAGException):
    """重量级资源（模型、连接）初始化或访问失败。"""
    pass


class CoreRuntimeError(BestRAGException):
    """Core 运行时错误（非配置、非 Provider、非资源类）。"""
    pass


class ServiceNotFoundError(BestRAGException):
    """Registry 中未找到指定服务。"""
    pass


# ── 业务模块异常 ──────────────────────────────────

class EmbeddingException(BestRAGException):
    """Embedding 模块异常。"""
    pass


class VectorStoreException(BestRAGException):
    """向量存储模块异常。"""
    pass


class RetrievalException(BestRAGException):
    """检索模块异常。"""
    pass


class RerankException(BestRAGException):
    """重排序模块异常。"""
    pass


class GenerationException(BestRAGException):
    """生成模块异常。"""
    pass
