"""SchemaTransformer — Schema 标准化转换器。

Phase 1 职责：
1. 补充 metadata.extra 溯源信息（source_file、document_id）
2. 如果 metadata.created_time 为空，补系统时间
3. 不修改已有字段，不校验 schema（Pydantic 负责）
"""

from copy import deepcopy
from datetime import datetime, timezone

from document.model import Document

from .base import BaseTransformer


class SchemaTransformer(BaseTransformer):
    """Schema 标准化转换器。

    对 Document 执行无损转换，只补充不修改。

    Usage::

        transformer = SchemaTransformer()
        normalized = transformer.transform(document)
    """

    def transform(self, document: Document) -> Document:
        metadata = document.metadata
        extra = deepcopy(metadata.extra)

        # 1) 补充溯源信息（不覆盖已有值）
        extra.setdefault("source_file", metadata.filename)
        extra.setdefault("document_id", document.id)

        # 2) 补齐 created_time（如果为空）
        created = metadata.created_time
        if created is None:
            created = datetime.now(timezone.utc)

        # 构建新的 metadata（extra 已更新）
        new_metadata = metadata.model_copy(update={
            "created_time": created,
            "extra": extra,
        })

        return Document(
            id=document.id,
            content=document.content,
            metadata=new_metadata,
        )
