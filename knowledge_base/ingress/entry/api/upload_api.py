"""FastAPI Upload 入口 — Web 端文件上传。

流程：
    Browser → HTTP Multipart → Upload API → IngressService → UploadAdapter → InputFile

依赖：FastAPI, python-multipart
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, File, UploadFile

from ...model.source import UploadSource
from ...service.ingress_service import IngressService

router = APIRouter(prefix="/ingress", tags=["ingress"])

# ---- 响应模型 ----

@dataclass
class InputFileResponse:
    """上传成功的响应体（避免暴露完整的 InputFile 内部字段）。"""
    id: str
    filename: str
    mime: str
    size: int
    checksum: str
    source: str

    @classmethod
    def from_input_file(cls, f):
        return cls(
            id=str(f.id),
            filename=f.filename,
            mime=f.mime,
            size=f.size,
            checksum=f.checksum,
            source=f.source.name,
        )


# ---- 全局服务实例（由应用启动时注入） ----

_service: Optional[IngressService] = None


def set_ingress_service(service: IngressService) -> None:
    """注入 IngressService 实例（由 main.py 在启动时调用）。"""
    global _service
    _service = service


def _get_service() -> IngressService:
    if _service is None:
        raise RuntimeError("IngressService 未初始化，请先调用 set_ingress_service()")
    return _service


# ---- 路由 ----

@router.post("/upload", response_model=InputFileResponse)
async def upload(file: UploadFile = File(...)):
    """上传单个文件 → 返回 InputFile 摘要。

    curl 示例::

        curl -F "file=@report.pdf" http://localhost:8000/ingress/upload
    """
    content = await file.read()
    source = UploadSource(
        filename=file.filename or "unknown",
        content=content,
    )
    svc = _get_service()
    input_file = svc.ingest(source)
    return InputFileResponse.from_input_file(input_file)
