"""WorkspaceManager — unified runtime file management for all BestRAG modules.

All file I/O paths MUST come from WorkspaceManager.
No module may decide its own file storage location.
"""

import shutil
from pathlib import Path

try:
    from .config import WorkspaceConfig, get_config
except ImportError:
    from config import WorkspaceConfig, get_config  # pragma: no cover


class WorkspaceManager:
    """Central authority for all workspace directories and file operations.

    Usage::

        wm = WorkspaceManager()          # uses default config
        wm = WorkspaceManager("/data")   # custom root
        path = wm.upload_path / "file.pdf"
    """

    def __init__(self, root: str | Path | None = None, config: WorkspaceConfig | None = None):
        if config is None:
            config = get_config().workspace
        self._config = config
        self._root = Path(root) if root else Path(config.root).resolve()

    # ---- directory getters ----

    @property
    def root(self) -> Path:
        return self._root

    @property
    def upload_path(self) -> Path:
        return self._ensure(self._root / self._config.upload)

    @property
    def document_path(self) -> Path:
        return self._ensure(self._root / self._config.document)

    @property
    def parser_path(self) -> Path:
        return self._ensure(self._root / self._config.parser)

    @property
    def chunk_path(self) -> Path:
        return self._ensure(self._root / self._config.chunk)

    @property
    def cache_path(self) -> Path:
        return self._ensure(self._root / self._config.cache)

    @property
    def export_path(self) -> Path:
        return self._ensure(self._root / self._config.export)

    @property
    def temp_path(self) -> Path:
        return self._ensure(self._root / self._config.temp)

    @property
    def logs_path(self) -> Path:
        return self._ensure(self._root / self._config.logs)

    # ---- file operations ----

    def save_upload(self, content: bytes, checksum: str, extension: str) -> Path:
        """Save uploaded file content as ``<checksum>.<ext>`` in upload/.

        Returns the full path to the saved file.
        """
        filename = f"{checksum}.{extension.lstrip('.')}"
        dest = self.upload_path / filename
        dest.write_bytes(content)
        return dest

    def remove(self, path: Path) -> None:
        """Remove a file from workspace."""
        if path.exists():
            path.unlink()

    def clean_temp(self) -> None:
        """Remove and recreate the temp directory."""
        p = self._root / self._config.temp
        if p.exists():
            shutil.rmtree(p)
        p.mkdir(parents=True, exist_ok=True)

    def init_all(self) -> None:
        """Create all workspace subdirectories (call once at startup)."""
        for attr in (
            "upload_path", "document_path", "parser_path", "chunk_path",
            "cache_path", "export_path", "temp_path", "logs_path",
        ):
            getattr(self, attr)  # property triggers _ensure

    # ---- internal ----

    def _ensure(self, path: Path) -> Path:
        path.mkdir(parents=True, exist_ok=True)
        return path
