"""CLI Import 入口 — 本地开发和批量导入。

流程：
    CLI → IngressService → LocalAdapter / FolderAdapter → InputFile

使用方式::

    bestrag ingest ./document.pdf           # 单文件
    bestrag ingest ./docs/ --recursive      # 目录批量
    bestrag ingest ./docs/ -r               # 同上

依赖：typer
"""

from pathlib import Path

import typer

from ..model.source import FolderSource, LocalSource
from ..service.ingress_service import IngressService

app = typer.Typer(
    name="bestrag",
    help="BestRAG — 企业知识库 RAG 框架",
)

# ---- 全局服务 ----

_service: IngressService | None = None


def set_ingress_service(service: IngressService) -> None:
    """注入 IngressService 实例。"""
    global _service
    _service = service


def _get_service() -> IngressService:
    global _service
    if _service is None:
        # 延迟初始化默认实例
        from core.workspace_manager import WorkspaceManager

        wm = WorkspaceManager()
        _service = IngressService(wm)
    return _service


# ---- 命令 ----

@app.command()
def ingest(
    path: str = typer.Argument(..., help="文件路径或目录路径"),
    recursive: bool = typer.Option(
        False, "--recursive", "-r", help="递归扫描目录下所有文件"
    ),
):
    """将外部文件导入 BestRAG 系统。

    单文件::

        bestrag ingest ./report.pdf

    目录批量::

        bestrag ingest ./docs/ --recursive
    """
    p = Path(path).resolve()

    if p.is_file():
        source = LocalSource(path=p)
        result = _get_service().ingest(source)
        _print_single(result)

    elif p.is_dir():
        source = FolderSource(directory=p, recursive=recursive)
        results = _get_service().ingest(source)
        _print_batch(results)

    else:
        typer.echo(f"错误: 路径不存在 — {p}", err=True)
        raise typer.Exit(code=1)


# ---- 输出 ----

def _print_single(input_file) -> None:
    """打印单个 InputFile 摘要。"""
    typer.echo(f"[OK] 导入成功: {input_file.filename}")
    typer.echo(f"   ID:       {input_file.id}")
    typer.echo(f"   类型:     {input_file.mime}")
    typer.echo(f"   大小:     {_human_size(input_file.size)}")
    typer.echo(f"   SHA256:   {input_file.checksum[:16]}...")
    typer.echo(f"   来源:     {input_file.source.name}")
    typer.echo(f"   路径:     {input_file.path}")


def _print_batch(input_files: list) -> None:
    """打印批量导入摘要。"""
    count = len(input_files)
    total_size = sum(f.size for f in input_files)
    typer.echo(f"[OK] 批量导入完成: {count} 个文件, 总计 {_human_size(total_size)}")
    for f in input_files:
        typer.echo(f"   • {f.filename}  ({f.mime}, {_human_size(f.size)})")


def _human_size(size: int) -> str:
    """字节数 → 人类可读大小。"""
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


if __name__ == "__main__":
    app()
