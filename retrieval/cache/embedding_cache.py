"""EmbeddingCache — Query Embedding 缓存（Redis）。

Key: hash(query + model_name + model_version)
特点：相同 query 跳过 Embedding 模型调用，直接返回缓存向量。
"""

import hashlib
import json
from typing import List, Optional

import redis

from core.config import get_config
from core.logger import get_logger

logger = get_logger(__name__)


class EmbeddingCache:
    """Embedding 缓存层 — Redis 后端。

    Usage::

        cache = EmbeddingCache()
        vec = cache.get(query)          # 命中则直接返回
        if vec is None:
            vec = model.embed(query)
            cache.set(query, vec)
    """

    def __init__(self, client: Optional[redis.Redis] = None):
        cfg = get_config().retrieval
        emb_cfg = get_config().embedding
        self._ttl = cfg.cache_ttl
        self._model_name = emb_cfg.model_name
        self._enabled = cfg.cache_enabled

        if client is None:
            self._redis = redis.Redis(
                host=cfg.redis_host,
                port=cfg.redis_port,
                db=cfg.redis_db,
                protocol=2,  # Redis 5.x 兼容
                decode_responses=True,
            )
        else:
            self._redis = client

    # ── 公开接口 ──────────────────────────────────

    def get(self, query: str, model_version: str = "v1") -> Optional[List[float]]:
        """获取缓存的 Embedding 向量，无命中返回 None。"""
        if not self._enabled:
            return None

        key = self._make_key(query, model_version)
        try:
            raw = self._redis.get(key)
            if raw:
                logger.debug(f"Embedding cache HIT: {key[:32]}...")
                return json.loads(raw)
            logger.debug(f"Embedding cache MISS: {key[:32]}...")
        except redis.RedisError as e:
            logger.warning(f"EmbeddingCache Redis 错误: {e}")
        return None

    def set(self, query: str, vector: List[float], model_version: str = "v1") -> None:
        """缓存 Embedding 向量。"""
        if not self._enabled:
            return

        key = self._make_key(query, model_version)
        try:
            self._redis.set(key, json.dumps(vector), ex=self._ttl)
            logger.debug(f"Embedding cache SET: {key[:32]}...")
        except redis.RedisError as e:
            logger.warning(f"EmbeddingCache SET 错误: {e}")

    def delete(self, query: str, model_version: str = "v1") -> None:
        """手动删除缓存。"""
        key = self._make_key(query, model_version)
        try:
            self._redis.delete(key)
        except redis.RedisError:
            pass

    # ── 内部 ──────────────────────────────────────

    def _make_key(self, query: str, model_version: str) -> str:
        raw = f"{query}|{self._model_name}|{model_version}"
        digest = hashlib.md5(raw.encode()).hexdigest()
        return f"bestrag:embcache:{digest}"
