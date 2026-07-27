"""Indexing 域异常。"""

from core.exception import CoreRuntimeError


class IndexingError(CoreRuntimeError):
    """索引过程中发生的错误（写入失败、Embedding 调用失败等）。"""
    pass
