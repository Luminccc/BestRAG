"""Ingress Entry Layer — CLI 入口。

Entry 负责：
- 接收外部请求（CLI / Watcher）
- 转换输入格式为 Source 对象
- 调用 IngressService

Entry 不负责：
- 文件保存
- 文件解析
- Document 生成

注意：API 入口已移至 knowledge_base/ingress/api/，不属于 entry 层。
"""

from .cli.import_cli import app as cli_app

__all__ = ["cli_app"]
