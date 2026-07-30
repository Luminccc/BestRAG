"""RepositoryRegistry — 数据仓库注册表。

管理 BaseRepository 子类的注册与发现，
用于 Service 层获取数据访问对象。
"""

from typing import Any, Dict

from core.registry.base import BaseRegistry


class RepositoryRegistry(BaseRegistry):
    """数据仓库注册表，存储 Repository 实例。"""

    def __init__(self):
        self._repos: Dict[str, Any] = {}

    def register(self, name: str, repo: Any) -> None:
        """注册 Repository 实例。"""
        self._repos[name] = repo

    def get(self, name: str) -> Any:
        """获取已注册的 Repository 实例。"""
        if name not in self._repos:
            raise KeyError(f"Repository '{name}' 未注册，可用: {list(self._repos)}")
        return self._repos[name]

    def has(self, name: str) -> bool:
        """检查 Repository 是否已注册。"""
        return name in self._repos

    def remove(self, name: str) -> None:
        """移除指定 Repository。"""
        self._repos.pop(name, None)

    def clear(self) -> None:
        """清空所有 Repository 注册。"""
        self._repos.clear()

    def list(self) -> list[str]:
        """列出所有已注册的 Repository 名称。"""
        return list(self._repos.keys())
