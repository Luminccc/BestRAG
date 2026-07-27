"""Core — BestRAG 基础运行层。

职责：
- 应用生命周期管理（Application）
- 全局配置管理（ConfigManager）
- Provider 注册与发现（ServiceRegistry）
- 重量级资源管理（ResourceManager）
- 统一日志（Logger）
- 统一异常（Exception）

所有业务模块（Document / Processor / Retrieval）通过 Core 获取实例和服务，
不负责创建实例或管理生命周期。
"""

from .config import (
    AppConfig,
    ConfigManager,
    CoreConfig,
    EmbeddingConfig,
    GenerationConfig,
    IndexingConfig,
    RetrievalConfig,
    RerankerConfig,
    VectorStoreConfig,
    WorkspaceConfig,
    get_config,
)
from .exception import (
    BestRAGException,
    ConfigError,
    CoreRuntimeError,
    EmbeddingException,
    GenerationException,
    ProviderError,
    RerankException,
    ResourceError,
    RetrievalException,
    ServiceNotFoundError,
    VectorStoreException,
)
from .logger import Logger, get_logger
from .provider import BaseProvider
from .registry import (
    clear_services,
    get_service,
    register_service,
    register_service_factory,
    unregister_service,
)
from .resource_manager import ResourceManager
from .utils import (
    calculate_md5,
    calculate_sha256,
    generate_id,
    get_current_timestamp,
    get_current_timestamp_ms,
    is_empty,
    safe_get_nested_value,
    truncate_text,
)

__all__ = [
    # Application (兼容入口 — 通过 core.app 延迟加载)
    "Application",
    # Config
    "AppConfig",
    "ConfigManager",
    "CoreConfig",
    "EmbeddingConfig",
    "RetrievalConfig",
    "RerankerConfig",
    "VectorStoreConfig",
    "WorkspaceConfig",
    "get_config",
    "GenerationConfig",
    "IndexingConfig",
    # Registry
    "register_service",
    "register_service_factory",
    "get_service",
    "unregister_service",
    "clear_services",
    # Logger
    "get_logger",
    "Logger",
    # Provider
    "BaseProvider",
    # Resource
    "ResourceManager",
    # Exception
    "BestRAGException",
    "ConfigError",
    "CoreRuntimeError",
    "EmbeddingException",
    "GenerationException",
    "ProviderError",
    "RerankException",
    "ResourceError",
    "RetrievalException",
    "ServiceNotFoundError",
    "VectorStoreException",
    # Utils
    "generate_id",
    "get_current_timestamp",
    "get_current_timestamp_ms",
    "calculate_md5",
    "calculate_sha256",
    "safe_get_nested_value",
    "truncate_text",
    "is_empty",
]


# 延迟加载 Application（避免循环导入：core → core.app → core.application → retrieval → core）
def __getattr__(name: str):
    if name == "Application":
        from .app import Application
        return Application
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
