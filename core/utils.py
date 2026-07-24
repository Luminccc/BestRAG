"""工具函数模块 — 提供通用的工具函数。

包括：
- 字符串处理
- 文件操作
- 时间处理
- 其他通用工具
"""

import hashlib
import time
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4


def generate_id() -> str:
    """生成唯一ID。"""
    return str(uuid4())


def get_current_timestamp() -> int:
    """获取当前时间戳（秒）。"""
    return int(time.time())


def get_current_timestamp_ms() -> int:
    """获取当前时间戳（毫秒）。"""
    return int(time.time() * 1000)


def calculate_md5(content: Union[str, bytes]) -> str:
    """计算MD5哈希值。"""
    if isinstance(content, str):
        content = content.encode('utf-8')
    return hashlib.md5(content).hexdigest()


def calculate_sha256(content: Union[str, bytes]) -> str:
    """计算SHA256哈希值。"""
    if isinstance(content, str):
        content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()


def safe_get_nested_value(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    """安全获取嵌套字典值。"""
    current = data
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本。"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def is_empty(value: Any) -> bool:
    """检查值是否为空。"""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, (list, tuple, dict, set)) and len(value) == 0:
        return True
    return False