"""v0.3 新增 — Cache 配置模型。"""

from dataclasses import dataclass, field


@dataclass
class CacheConfig:
    """缓存配置。"""
    provider: str = "memory"        # memory / redis / local
    ttl: int = 3600                 # 默认 TTL（秒）
    max_size: int = 1000            # 最大缓存条目数
