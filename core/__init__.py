"""Core — BestRAG 基础设施层。

提供所有模块共同依赖的基础能力：
- 配置管理
- 依赖注入/服务注册
- 日志记录
- 异常处理
- 工具函数

Core 的职责不是管理模块间的服务链路，而是提供模块共同依赖的基础能力。
业务链路本身（如上传、解析、调度、检索）仍留在各自的业务模块中。
"""

from .config import get_config, CoreConfig, RetrievalConfig
from .registry import register_service, register_service_factory, get_service, unregister_service
from .logger import get_logger, Logger
from .exception import (
    BestRAGException,
    ConfigException,
    ServiceNotFoundException,
    EmbeddingException,
    VectorStoreException,
    RetrievalException,
    RerankException
)
from .utils import (
    generate_id,
    get_current_timestamp,
    get_current_timestamp_ms,
    calculate_md5,
    calculate_sha256,
    safe_get_nested_value,
    truncate_text,
    is_empty
)

__all__ = [
    "get_config",
    "CoreConfig",
    "RetrievalConfig",
    "register_service",
    "register_service_factory",
    "get_service",
    "unregister_service",
    "get_logger",
    "Logger",
    "BestRAGException",
    "ConfigException",
    "ServiceNotFoundException",
    "EmbeddingException",
    "VectorStoreException",
    "RetrievalException",
    "RerankException",
    "generate_id",
    "get_current_timestamp",
    "get_current_timestamp_ms",
    "calculate_md5",
    "calculate_sha256",
    "safe_get_nested_value",
    "truncate_text",
    "is_empty"
]