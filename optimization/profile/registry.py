"""ProfileRegistry — 策略配置注册表。

管理内置 Profile 和用户自定义 Profile。
"""

from typing import Dict, List, Optional

from optimization.profile.model import RAGProfile, DEFAULT_PROFILE


class ProfileRegistry:
    """Profile 注册表。

    用法::

        registry = ProfileRegistry()
        registry.register(tech_profile)
        profile = registry.get("technical_doc")
    """

    def __init__(self):
        self._profiles: Dict[str, RAGProfile] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        from optimization.profile.model import (
            DEFAULT_PROFILE,
            FAQ_PROFILE,
            LONG_DOC_PROFILE,
            PAPER_PROFILE,
            TECHNICAL_DOC_PROFILE,
        )
        for p in [DEFAULT_PROFILE, TECHNICAL_DOC_PROFILE, FAQ_PROFILE, LONG_DOC_PROFILE, PAPER_PROFILE]:
            self._profiles[p.name] = p

    def register(self, profile: RAGProfile) -> None:
        """注册 Profile。"""
        self._profiles[profile.name] = profile

    def get(self, name: str) -> Optional[RAGProfile]:
        """按名称获取 Profile。"""
        return self._profiles.get(name)

    def list(self) -> List[RAGProfile]:
        """列出所有 Profile。"""
        return list(self._profiles.values())

    def list_names(self) -> List[str]:
        """列出所有 Profile 名称。"""
        return list(self._profiles.keys())

    def remove(self, name: str) -> None:
        """移除 Profile。"""
        self._profiles.pop(name, None)
