"""配置管理模块 — 提供统一的配置读取和管理能力。

支持多种配置源：
- 默认配置
- 环境变量覆盖
- YAML 配置文件
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


@dataclass
class RetrievalConfig:
    """Retrieval 模块配置。"""
    # Embedding 配置
    embedding_model: str = "BAAI/bge-base-en-v1.5"
    embedding_dim: int = 1024  # BGE-M3 默认 1024 维
    embedding_api_url: str = "http://127.0.0.1:8001/embed"  # BGE-M3 API 地址，非空时优先使用 API 而非本地模型

    # VectorStore 配置
    vectorstore_type: str = "milvus"
    milvus_host: str = "127.0.0.1"
    milvus_port: int = 19530
    milvus_collection_prefix: str = "bestrag"

    # Rerank 配置
    rerank_model: str = "BAAI/bge-reranker-base"
    rerank_api_url: str = "http://127.0.0.1:8002/rerank"  # BGE-Rerank API 地址，非空时优先使用 API 而非本地模型

    # 其他配置
    top_k: int = 10


@dataclass
class CoreConfig:
    """Core 配置。"""
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)


class ConfigManager:
    """配置管理器 — 统一配置读取和管理。"""

    _instance: Optional['ConfigManager'] = None
    _config: Optional[CoreConfig] = None

    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_config(self) -> CoreConfig:
        """获取配置实例。"""
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def _load_config(self) -> CoreConfig:
        """加载配置。"""
        # 1. 默认配置
        config = CoreConfig()

        # 2. 环境变量覆盖
        self._load_from_env(config)

        # 3. YAML 配置文件覆盖
        self._load_from_yaml(config)

        return config

    def _load_from_env(self, config: CoreConfig) -> None:
        """从环境变量加载配置。"""
        # Retrieval 配置
        retrieval = config.retrieval

        # Embedding 配置
        embedding_model = os.environ.get("BESTRAG_EMBEDDING_MODEL")
        if embedding_model:
            retrieval.embedding_model = embedding_model

        embedding_dim = os.environ.get("BESTRAG_EMBEDDING_DIM")
        if embedding_dim:
            retrieval.embedding_dim = int(embedding_dim)

        embedding_api_url = os.environ.get("BESTRAG_EMBEDDING_API_URL")
        if embedding_api_url:
            retrieval.embedding_api_url = embedding_api_url

        # VectorStore 配置
        vectorstore_type = os.environ.get("BESTRAG_VECTORSTORE_TYPE")
        if vectorstore_type:
            retrieval.vectorstore_type = vectorstore_type

        milvus_host = os.environ.get("BESTRAG_MILVUS_HOST")
        if milvus_host:
            retrieval.milvus_host = milvus_host

        milvus_port = os.environ.get("BESTRAG_MILVUS_PORT")
        if milvus_port:
            retrieval.milvus_port = int(milvus_port)

        milvus_collection_prefix = os.environ.get("BESTRAG_MILVUS_COLLECTION_PREFIX")
        if milvus_collection_prefix:
            retrieval.milvus_collection_prefix = milvus_collection_prefix

        # Rerank 配置
        rerank_model = os.environ.get("BESTRAG_RERANK_MODEL")
        if rerank_model:
            retrieval.rerank_model = rerank_model

        rerank_api_url = os.environ.get("BESTRAG_RERANK_API_URL")
        if rerank_api_url:
            retrieval.rerank_api_url = rerank_api_url

        # 其他配置
        top_k = os.environ.get("BESTRAG_TOP_K")
        if top_k:
            retrieval.top_k = int(top_k)

    def _load_from_yaml(self, config: CoreConfig) -> None:
        """从 YAML 配置文件加载配置。"""
        if not HAS_YAML:
            return

        yaml_path = Path(os.environ.get("BESTRAG_CONFIG", "config.yaml"))
        if not yaml_path.exists():
            return

        try:
            with open(yaml_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                return

            # Retrieval 配置
            retrieval_data = data.get("retrieval", {})
            if retrieval_data:
                retrieval = config.retrieval

                # Embedding 配置
                if "embedding_model" in retrieval_data:
                    retrieval.embedding_model = retrieval_data["embedding_model"]
                if "embedding_dim" in retrieval_data:
                    retrieval.embedding_dim = retrieval_data["embedding_dim"]
                if "embedding_api_url" in retrieval_data:
                    retrieval.embedding_api_url = retrieval_data["embedding_api_url"]

                # VectorStore 配置
                if "vectorstore_type" in retrieval_data:
                    retrieval.vectorstore_type = retrieval_data["vectorstore_type"]
                if "milvus_host" in retrieval_data:
                    retrieval.milvus_host = retrieval_data["milvus_host"]
                if "milvus_port" in retrieval_data:
                    retrieval.milvus_port = retrieval_data["milvus_port"]
                if "milvus_collection_prefix" in retrieval_data:
                    retrieval.milvus_collection_prefix = retrieval_data["milvus_collection_prefix"]

                # Rerank 配置
                if "rerank_model" in retrieval_data:
                    retrieval.rerank_model = retrieval_data["rerank_model"]
                if "rerank_api_url" in retrieval_data:
                    retrieval.rerank_api_url = retrieval_data["rerank_api_url"]

                # 其他配置
                if "top_k" in retrieval_data:
                    retrieval.top_k = retrieval_data["top_k"]
        except Exception:
            # 配置文件解析失败时忽略
            pass


# 全局配置管理器实例
_config_manager = ConfigManager()


def get_config() -> CoreConfig:
    """获取全局配置实例。"""
    return _config_manager.get_config()