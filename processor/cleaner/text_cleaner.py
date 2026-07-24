"""TextCleaner — 通用文本清洗器。

处理项：
1. 多余空格规范化（连续空白 → 单个空格）
2. 多余换行规范化（连续 3+ 换行 → 2 换行）
3. 控制字符移除（\\x00-\\x1f 除 \\n \\t）
4. 首尾空白裁剪
"""

import re
from copy import deepcopy

from document.model import Document

from .base import BaseCleaner

# 控制字符（保留 \\n 和 \\t，移除其余 \\x00-\\x1f 范围字符）
_CONTROL_PATTERN = re.compile(
    r"[\x00-\x08\x0b\x0c\x0e-\x1f]"
)

# 连续 3 个及以上换行 → 2 个换行
_MULTI_NEWLINE_PATTERN = re.compile(r"\n{3,}")


class TextCleaner(BaseCleaner):
    """通用文本清洗器，执行标准的文本规范化流程。

    Usage::

        cleaner = TextCleaner()
        clean_doc = cleaner.clean(document)
    """

    def clean(self, document: Document) -> Document:
        original = document.content
        original_len = len(original)

        # 1) 移除控制字符
        content = _CONTROL_PATTERN.sub("", original)

        # 2) 连续空格规范化
        content = re.sub(r"[ \t]+", " ", content)

        # 3) 连续换行规范化
        content = _MULTI_NEWLINE_PATTERN.sub("\n\n", content)

        # 4) 每行首尾去空格（保留换行结构）
        content = "\n".join(line.strip() for line in content.splitlines())

        # 5) 整体首尾裁剪
        content = content.strip()

        cleaned_len = len(content)

        # 将清洗信息写入 metadata.extra
        extra = deepcopy(document.metadata.extra)
        extra["cleaned"] = True
        extra["original_length"] = original_len
        extra["cleaned_length"] = cleaned_len

        # 构建新的 Document（保留原 id 和基本元数据）
        new_metadata = document.metadata.model_copy(update={"extra": extra})

        return Document(
            id=document.id,
            content=content,
            metadata=new_metadata,
        )
