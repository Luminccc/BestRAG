"""BaseModel — 所有业务 Model 的父类。

职责：
- 提供唯一 ID（自动生成或外部传入）
- 记录创建/更新时间戳
- 统一序列化（to_dict / to_json）
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional

from core.utils import generate_id


class BaseModel:
    """业务模型基类。

    用法::

        class Document(BaseModel):
            def __init__(self, title: str, content: str, **kwargs):
                super().__init__(**kwargs)
                self.title = title
                self.content = content

        doc = Document(title="test", content="hello")
        doc.to_dict()  # {"id": "...", "created_at": "...", "title": "test", ...}
    """

    id: str
    created_at: datetime
    updated_at: datetime

    def __init__(
        self,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs: Any,
    ):
        self.id = id or generate_id()
        now = datetime.now()
        self.created_at = created_at or now
        self.updated_at = updated_at or now

        # 剩余 kwargs 直接设为属性
        for k, v in kwargs.items():
            setattr(self, k, v)

    # ── 序列化 ──────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，datetime 自动转 ISO 格式。"""
        result: Dict[str, Any] = {}
        for k, v in self.__dict__.items():
            if isinstance(v, datetime):
                result[k] = v.isoformat()
            elif isinstance(v, BaseModel):
                result[k] = v.to_dict()
            elif isinstance(v, list):
                result[k] = [
                    item.to_dict() if isinstance(item, BaseModel) else item
                    for item in v
                ]
            else:
                result[k] = v
        return result

    def to_json(self, **kwargs: Any) -> str:
        """转换为 JSON 字符串。"""
        return json.dumps(self.to_dict(), ensure_ascii=False, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id!r})"
