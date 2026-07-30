"""Metadata — 通用元数据容器。

用于携带模型附属信息（来源、标签、自定义字段等），
不参与核心业务逻辑，仅作为信息载体。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Metadata:
    """通用元数据容器。

    Usage::

        meta = Metadata(source="web", tags=["rag", "v0.3"])
        meta.to_dict()
    """

    source: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """合并为完整字典。"""
        return {
            "source": self.source,
            "tags": self.tags,
            **self.extra,
        }
