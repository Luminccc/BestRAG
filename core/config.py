"""配置管理模块 — 统一配置入口。

PDR 配置层次::

    app / database / model / embedding / vectorstore / retrieval

所有模块通过 `get_config()` 获取配置，禁止 os.getenv() / yaml.load() 直接读取。

环境变量覆盖优先级：默认值 < YAML 文件 < 环境变量
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    yaml = None  # type: ignore


# ═══════════════════════════════════════════════════
# 配置数据类
# ═══════════════════════════════════════════════════

@dataclass
class AppConfig:
    """应用基础配置。"""
    name: str = "BestRAG"
    version: str = "0.1.0"
    debug: bool = False


@dataclass
class WorkspaceConfig:
    """工作空间路径配置。"""
    root: str = "./workspace"
    upload: str = "upload"
    document: str = "document"
    parser: str = "parser"
    chunk: str = "chunk"
    cache: str = "cache"
    export: str = "export"
    temp: str = "temp"
    logs: str = "logs"


@dataclass
class EmbeddingConfig:
    """Embedding 模型配置。"""
    provider: str = "bge"
    model_name: str = "BAAI/bge-m3"
    dim: int = 1024
    api_url: str = "http://127.0.0.1:8001/embed"
    # api_url 非空时优先使用 API 而非本地模型


@dataclass
class VectorStoreConfig:
    """向量存储配置。"""
    provider: str = "milvus"
    host: str = "127.0.0.1"
    port: int = 19530
    collection_prefix: str = "bestrag"


@dataclass
class RerankerConfig:
    """重排序模型配置。"""
    provider: str = "bge"
    model_name: str = "BAAI/bge-reranker-base"
    api_url: str = "http://127.0.0.1:8002/rerank"


@dataclass
class RetrievalConfig:
    """检索配置。"""
    top_k: int = 10
    strategy: str = "hybrid"           # "vector" / "bm25" / "hybrid"
    hybrid_vector_weight: float = 0.7
    hybrid_keyword_weight: float = 0.3
    cache_enabled: bool = True
    cache_backend: str = "redis"        # "redis" / "memory"
    cache_ttl: int = 3600               # 秒
    filter_enabled: bool = True
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    redis_db: int = 0
    index_version: str = "v1"           # 索引版本号，变更时缓存自动失效


@dataclass
class IndexingConfig:
    """索引配置。"""
    batch_size: int = 32
    auto_commit: bool = True


@dataclass
class GenerationConfig:
    """生成配置。"""
    provider: str = "openai"            # LLM Provider 类型
    model_name: str = "gpt-4o-mini"    # 默认模型名
    temperature: float = 0.2           # 生成温度
    api_key: str = ""                  # API Key（也可通过环境变量 BESTRAG_LLM_API_KEY 设置）
    base_url: str = "https://api.openai.com/v1"  # OpenAI 兼容端点
    system_prompt: str = ""            # 默认 system prompt（空则用内置值）
    max_tokens: int = 2048             # 最大输出 token


@dataclass
class CoreConfig:
    """Core 总配置 — 聚合所有子配置。"""
    app: AppConfig = field(default_factory=AppConfig)
    workspace: WorkspaceConfig = field(default_factory=WorkspaceConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    vectorstore: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    reranker: RerankerConfig = field(default_factory=RerankerConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    indexing: IndexingConfig = field(default_factory=IndexingConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)


# ═══════════════════════════════════════════════════
# ConfigManager
# ═══════════════════════════════════════════════════

class ConfigManager:
    """统一配置管理器（单例）。"""

    _instance: Optional["ConfigManager"] = None
    _config: Optional[CoreConfig] = None

    def __new__(cls) -> "ConfigManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get(self) -> CoreConfig:
        """获取完整配置。"""
        if self._config is None:
            self._config = self._load()
        return self._config

    def reset(self) -> None:
        """重置配置（测试用）。"""
        self._config = None

    # ── 加载流水线 ──────────────────────────────

    def _load(self) -> CoreConfig:
        config = CoreConfig()
        self._load_yaml(config)
        self._load_env(config)
        return config

    def _load_yaml(self, config: CoreConfig) -> None:
        if not HAS_YAML:
            return
        path = Path(os.environ.get("BESTRAG_CONFIG", "config.yaml"))
        if not path.exists():
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            return

        # 扁平 + 嵌套两种 YAML 写法兼容
        for section in ("workspace", "embedding", "vectorstore", "reranker", "retrieval", "indexing", "generation", "app"):
            raw = data.get(section, {})
            if isinstance(raw, dict):
                _apply_fields(getattr(config, section), raw)

    def _load_env(self, config: CoreConfig) -> None:
        # App
        env_override(config.app, "name", "BESTRAG_APP_NAME")
        env_override(config.app, "debug", "BESTRAG_DEBUG", cast=bool)

        # Workspace
        env_override(config.workspace, "root", "BESTRAG_WORKSPACE_ROOT")

        # Embedding
        env_override(config.embedding, "provider", "BESTRAG_EMBEDDING_PROVIDER")
        env_override(config.embedding, "model_name", "BESTRAG_EMBEDDING_MODEL")
        env_override(config.embedding, "dim", "BESTRAG_EMBEDDING_DIM", cast=int)
        env_override(config.embedding, "api_url", "BESTRAG_EMBEDDING_API_URL")

        # VectorStore
        env_override(config.vectorstore, "provider", "BESTRAG_VECTORSTORE_TYPE")
        env_override(config.vectorstore, "host", "BESTRAG_MILVUS_HOST")
        env_override(config.vectorstore, "port", "BESTRAG_MILVUS_PORT", cast=int)
        env_override(config.vectorstore, "collection_prefix", "BESTRAG_MILVUS_COLLECTION_PREFIX")

        # Reranker
        env_override(config.reranker, "provider", "BESTRAG_RERANKER_PROVIDER")
        env_override(config.reranker, "model_name", "BESTRAG_RERANK_MODEL")
        env_override(config.reranker, "api_url", "BESTRAG_RERANK_API_URL")

        # Retrieval
        env_override(config.retrieval, "top_k", "BESTRAG_TOP_K", cast=int)
        env_override(config.retrieval, "strategy", "BESTRAG_RETRIEVAL_STRATEGY")
        env_override(config.retrieval, "cache_enabled", "BESTRAG_CACHE_ENABLED", cast=bool)
        env_override(config.retrieval, "index_version", "BESTRAG_INDEX_VERSION")

        # Indexing
        env_override(config.indexing, "batch_size", "BESTRAG_INDEXING_BATCH_SIZE", cast=int)
        env_override(config.indexing, "auto_commit", "BESTRAG_INDEXING_AUTO_COMMIT", cast=bool)

        # Generation
        env_override(config.generation, "model_name", "BESTRAG_LLM_MODEL")
        env_override(config.generation, "api_key", "BESTRAG_LLM_API_KEY")
        env_override(config.generation, "base_url", "BESTRAG_LLM_BASE_URL")
        env_override(config.generation, "temperature", "BESTRAG_LLM_TEMPERATURE", cast=float)


# ═══════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════

def _apply_fields(target: object, values: Dict[str, Any]) -> None:
    """安全地将 dict 字段写入 dataclass，忽略不存在的字段。"""
    for k, v in values.items():
        if hasattr(target, k):
            setattr(target, k, v)


def env_override(target: object, field_name: str, env_var: str, cast=None) -> None:
    """环境变量覆盖 dataclass 字段。"""
    val = os.environ.get(env_var)
    if val is None or val == "":
        return
    if cast:
        try:
            val = cast(val)
        except (ValueError, TypeError):
            return
    setattr(target, field_name, val)


# ═══════════════════════════════════════════════════
# 全局访问入口
# ═══════════════════════════════════════════════════

_manager = ConfigManager()


def get_config() -> CoreConfig:
    """获取全局配置实例（统一入口）。

    Usage::

        from core.config import get_config
        cfg = get_config()
        print(cfg.embedding.model_name)
        print(cfg.workspace.root)
    """
    return _manager.get()
