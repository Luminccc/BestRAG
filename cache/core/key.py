"""CacheKey — 缓存 Key 生成器。

提供统一的 Key 生成机制，支持命名空间和参数签名。
"""

import hashlib
import json
from typing import Any, Dict, Optional


class CacheKey:
    """缓存 Key 生成器。

    Usage::

        key = CacheKey.make("query", query="什么是 RAG?", top_k=5)
        # -> "cache:query:a1b2c3d4..."
    """

    @staticmethod
    def make(namespace: str, **params: Any) -> str:
        """生成缓存 Key。

        Args:
            namespace: 命名空间（如 "query", "embedding", "retrieval"）。
            **params: 用于生成签名的参数。

        Returns:
            带命名空间的缓存 Key。
        """
        raw = json.dumps(params, sort_keys=True, ensure_ascii=False)
        digest = hashlib.md5(raw.encode()).hexdigest()
        return f"bestrag:{namespace}:{digest}"

    @staticmethod
    def from_dict(namespace: str, params: Dict[str, Any]) -> str:
        """从字典生成 Key。"""
        return CacheKey.make(namespace, **params)
