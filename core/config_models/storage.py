"""v0.3 新增 — Storage 配置模型。"""

from dataclasses import dataclass, field


@dataclass
class StorageConfig:
    """存储配置。"""
    provider: str = "local"         # local / s3 / minio
    base_path: str = "./data"       # 本地存储路径
