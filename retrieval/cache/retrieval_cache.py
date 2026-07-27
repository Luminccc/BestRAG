"""RetrievalCache — 检索结果缓存（Redis）。

Key: hash(query + strategy + top_k + filter + index_version)
特点：index_version 变更时自动失效，避免知识库更新后返回旧结果。
"""

import hashlib
import json
from typing import Any, Dict, List, Optional
from uuid import uuid4

import redis

from core.config import get_config
from core.logger import get_logger
from retrieval.retriever.model import RetrievalResult

logger = get_logger(__name__)


class RetrievalCache:
    """检索结果缓存 — Redis 后端，Index-aware Key。

    Usage::

        cache = RetrievalCache()
        results = cache.get(query, strategy, top_k, filters)
        if results is None:
            results = do_retrieval(...)
            cache.set(query, strategy, top_k, filters, results)
    """

    def __init__(self, client: Optional[redis.Redis] = None):
        cfg = get_config().retrieval
        self._ttl = cfg.cache_ttl
        self._enabled = cfg.cache_enabled
        self._index_version = cfg.index_version

        if client is None:
            self._redis = redis.Redis(
                host=cfg.redis_host,
                port=cfg.redis_port,
                db=cfg.redis_db,
                protocol=2,
                decode_responses=True,
            )
        else:
            self._redis = client

    # ── 公开接口 ──────────────────────────────────

    def get(
        self,
        query: str,
        strategy: str = "hybrid",
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Optional[List[RetrievalResult]]:
        """获取缓存结果，无命中返回 None。"""
        if not self._enabled:
            return None

        key = self._make_key(query, strategy, top_k, filters)
        try:
            raw = self._redis.get(key)
            if raw:
                logger.debug(f"Retrieval cache HIT: {key[:32]}...")
                items = json.loads(raw)
                return [RetrievalResult(**r) for r in items]
            logger.debug(f"Retrieval cache MISS: {key[:32]}...")
        except redis.RedisError as e:
            logger.warning(f"RetrievalCache Redis 错误: {e}")
        return None

    def set(
        self,
        query: str,
        strategy: str,
        top_k: int,
        filters: Optional[Dict[str, Any]],
        results: List[RetrievalResult],
    ) -> None:
        """缓存检索结果。"""
        if not self._enabled:
            return

        key = self._make_key(query, strategy, top_k, filters)
        items = [r.model_dump() for r in results]
        try:
            self._redis.set(key, json.dumps(items, ensure_ascii=False), ex=self._ttl)
            logger.debug(f"Retrieval cache SET: {key[:32]}...")
        except redis.RedisError as e:
            logger.warning(f"RetrievalCache SET 错误: {e}")

    def delete(
        self,
        query: str,
        strategy: str,
        top_k: int,
        filters: Optional[Dict[str, Any]],
    ) -> None:
        """手动删除缓存。"""
        key = self._make_key(query, strategy, top_k, filters)
        try:
            self._redis.delete(key)
        except redis.RedisError:
            pass

    # ── 内部 ──────────────────────────────────────

    def _make_key(
        self,
        query: str,
        strategy: str,
        top_k: int,
        filters: Optional[Dict[str, Any]],
    ) -> str:
        # filter dict 转排序字符串保证一致性
        filter_str = json.dumps(filters, sort_keys=True) if filters else "{}"
        raw = f"{query}|{strategy}|{top_k}|{filter_str}|{self._index_version}"
        digest = hashlib.md5(raw.encode()).hexdigest()
        return f"bestrag:retcache:{digest}"
