"""CacheConfigV3 — v0.3 Phase 5 缓存配置模型。"""

from dataclasses import dataclass, field


@dataclass
class CacheProviderConfig:
    """缓存 Provider 配置。"""
    type: str = "memory"  # memory / redis / local


@dataclass
class CacheTypeConfig:
    """单类型缓存配置。"""
    enabled: bool = True
    ttl: int = 3600


@dataclass
class CacheConfigV3:
    """缓存总体配置。"""
    enabled: bool = True
    provider: CacheProviderConfig = field(default_factory=CacheProviderConfig)
    query_cache: CacheTypeConfig = field(default_factory=lambda: CacheTypeConfig(ttl=3600))
    embedding_cache: CacheTypeConfig = field(default_factory=lambda: CacheTypeConfig(ttl=86400))
    retrieval_cache: CacheTypeConfig = field(default_factory=lambda: CacheTypeConfig(ttl=3600))
