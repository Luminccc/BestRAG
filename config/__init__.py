"""BestRAG configuration — all runtime settings, including Workspace paths.

Paths are relative to the project root unless absolute.
Override via environment variables or a local config.yaml.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class WorkspaceConfig:
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
class Config:
    workspace: WorkspaceConfig = field(default_factory=WorkspaceConfig)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Config":
        """Load config from a YAML file (requires PyYAML)."""
        import yaml  # type: ignore

        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        ws = data.get("workspace", {})
        return cls(workspace=WorkspaceConfig(**{k: v for k, v in ws.items() if k in WorkspaceConfig.__dataclass_fields__}))

    @classmethod
    def from_env(cls) -> "Config":
        """Load workspace root from BESTRAG_WORKSPACE_ROOT env var."""
        root = os.environ.get("BESTRAG_WORKSPACE_ROOT", "")
        if root:
            return cls(workspace=WorkspaceConfig(root=root))
        return cls()


# Singleton
_config: Config | None = None


def get_config() -> Config:
    global _config
    if _config is None:
        yaml_path = Path(os.environ.get("BESTRAG_CONFIG", "config.yaml"))
        if yaml_path.exists():
            _config = Config.from_yaml(yaml_path)
        else:
            _config = Config.from_env()
    return _config
