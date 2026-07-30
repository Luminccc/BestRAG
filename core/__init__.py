"""Core — BestRAG 基础运行层。

职责：
- 应用生命周期管理（Application）
- 全局配置管理（ConfigManager）
- Provider 注册与发现（RegistryCenter）
- 重量级资源管理（ResourceManager）
- 统一日志（Logger）
- 统一异常（Exception）

所有业务模块（Document / Processor / Retrieval）通过 Core 获取实例和服务，
不负责创建实例或管理生命周期。

v0.3 新增：
- BaseModel / Metadata  — 统一模型基类
- BaseService           — 统一服务基类
- BaseRepository        — 统一数据仓库基类
- BaseCacheProvider     — 缓存 Provider
- BaseStorageProvider   — 存储 Provider
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
from .provider import (
    BaseEmbeddingProvider,
    BaseLLMProvider,
    BaseProvider,
    BaseRerankerProvider,
    BaseSimilarityProvider,
    CosineSimilarityProvider,
    JaccardSimilarityProvider,
    ProviderFactory,
    # v0.3
    BaseCacheProvider,
    BaseStorageProvider,
)
from .registry import (
    clear_services,
    get_service,
    register_service,
    register_service_factory,
    unregister_service,
)
from .registry.center import RegistryCenter, get_registry
from .resource_manager import ResourceManager
from .strategy import (
    BaseChunkStrategy,
    BaseFusionStrategy,
    BaseRetrievalStrategy,
    BaseStrategy,
    StrategyFactory,
    StrategyPipeline,
)
from .strategy.fusion import RRFFusionStrategy, WeightedFusionStrategy
from .strategy.fusion.base import BaseFusionStrategy as FusionStrategyBase
from .strategy.query import (
    BaseQueryRewriteStrategy,
    LLMQueryRewriteStrategy,
    SimpleQueryRewriteStrategy,
)
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

# v0.2 新增配置模型
from .config_models.evaluation import EvaluationConfig
from .config_models.retrieval import (
    FusionConfig,
    QueryRewriteConfig,
    RetrieverPipelineConfig,
    RetrievalPipelineConfig,
)
from .config_models.strategy import ChunkStrategyConfig, StrategyConfig

# v0.3 新增
from .models import BaseModel, Metadata
from .service import BaseService
from .repository import BaseRepository
from .config_models.trace import TraceConfig
from .config_models.cache import CacheConfig
from .config_models.storage import StorageConfig

# v0.3 Phase 1 新增
from .config_models.knowledge import KnowledgeConfig, IndexConfig

# v0.3 Phase 3 新增
from .config_models.evaluation_v3 import EvaluationConfigV3

# v0.3 Phase 4 新增
from .config_models.retrieval_optimization import RetrievalOptimizationConfig

# v0.3 Phase 5 新增
from .config_models.cache_v3 import CacheConfigV3

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
    "RegistryCenter",
    "get_registry",
    # v0.2 Strategy Framework
    "BaseStrategy",
    "BaseChunkStrategy",
    "BaseRetrievalStrategy",
    "BaseFusionStrategy",
    "FusionStrategyBase",
    "StrategyPipeline",
    "StrategyFactory",
    "WeightedFusionStrategy",
    "RRFFusionStrategy",
    # Query Strategy
    "BaseQueryRewriteStrategy",
    "SimpleQueryRewriteStrategy",
    "LLMQueryRewriteStrategy",
    # Logger
    "get_logger",
    "Logger",
    # Provider
    "BaseProvider",
    "BaseEmbeddingProvider",
    "BaseSimilarityProvider",
    "BaseRerankerProvider",
    "BaseLLMProvider",
    "BaseCacheProvider",
    "BaseStorageProvider",
    "ProviderFactory",
    "JaccardSimilarityProvider",
    "CosineSimilarityProvider",
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
    # v0.2 Config Models
    "StrategyConfig",
    "ChunkStrategyConfig",
    "RetrievalPipelineConfig",
    "RetrieverPipelineConfig",
    "FusionConfig",
    "QueryRewriteConfig",
    "EvaluationConfig",
    # v0.3 Core
    "BaseModel",
    "Metadata",
    "BaseService",
    "BaseRepository",
    # v0.3 Config
    "TraceConfig",
    "CacheConfig",
    "StorageConfig",
    # v0.3 Phase 1 Config
    "KnowledgeConfig",
    "IndexConfig",
    # v0.3 Phase 3 Config
    "EvaluationConfigV3",
    # v0.3 Phase 4 Config
    "RetrievalOptimizationConfig",
    # v0.3 Phase 5 Config
    "CacheConfigV3",
]


# 延迟加载 Application（避免循环导入：core → core.app → core.application → retrieval → core）
def __getattr__(name: str):
    if name == "Application":
        from .app import Application
        return Application
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
