"""Validation API — FastAPI 验证入口。

提供：
- POST /validation/document             单文件验证
- POST /validation/document/all         全量回归验证
- POST /validation/processor/cleaner    Cleaner 验证
- POST /validation/retrieval/embedding  Embedding 验证
- POST /validation/retrieval/vectorstore VectorStore 验证
- POST /validation/retrieval/search     Retrieval 验证
- POST /validation/retrieval/rerank     Rerank 验证
"""

from fastapi import APIRouter, Body, Depends

from validation.model import ValidationReport
from validation.service import ValidationService

router = APIRouter(prefix="/validation", tags=["validation"])

# ---- 依赖注入 ----

_service: ValidationService | None = None


def _get_service() -> ValidationService:
    if _service is None:
        raise RuntimeError("ValidationService 未初始化，请在 main.py 中调用 init_validation_service()")
    return _service


def init_validation_service(svc: ValidationService) -> None:
    """初始化 ValidationService（由 main.py 启动时调用一次）。"""
    global _service
    _service = svc


# ---- 路由 ----

@router.post("/document", response_model=ValidationReport)
async def validate_document(
    file_path: str = Body(..., embed=True),
    svc: ValidationService = Depends(_get_service),
):
    """验证单个文件的 Document 链路是否正常。

    Request body (JSON)::

        {"file_path": "/data/test.pdf"}
    """
    return svc.validate_document(file_path)


@router.post("/document/all", response_model=list[ValidationReport])
async def validate_all_documents(
    svc: ValidationService = Depends(_get_service),
):
    """执行全量回归验证。

    自动生成测试文件，覆盖所有受支持格式和异常场景。
    用于发布前回归测试。
    """
    return svc.validate_all()


@router.post("/processor/cleaner", response_model=ValidationReport)
async def validate_processor_cleaner(
    file_path: str = Body(..., embed=True),
    svc: ValidationService = Depends(_get_service),
):
    """验证 Cleaner 链路：Document → Cleaner → Clean Document。

    Request body (JSON)::

        {"file_path": "/data/test.pdf"}
    """
    return svc.validate_cleaner(file_path)


@router.post("/processor/pipeline", response_model=ValidationReport)
async def validate_processor_pipeline(
    file_path: str = Body(...),
    strategy: str = Body("recursive"),
    svc: ValidationService = Depends(_get_service),
):
    """验证完整 Pipeline：Document → Cleaner → Chunker → Transformer。

    Request body (JSON)::

        {"file_path": "/data/test.pdf", "strategy": "recursive"}
    """
    return svc.validate_pipeline(file_path, strategy)


@router.post("/processor/chunk", response_model=ValidationReport)
async def validate_processor_chunk(
    file_path: str = Body(...),
    strategy: str = Body("recursive"),
    svc: ValidationService = Depends(_get_service),
):
    """验证 Chunk 链路：Clean Document → ChunkService → Chunk[]。

    Request body (JSON)::

        {"file_path": "/data/test.pdf", "strategy": "recursive"}
    """
    return svc.validate_chunker(file_path, strategy)


@router.post("/processor/transformer", response_model=ValidationReport)
async def validate_processor_transformer(
    file_path: str = Body(..., embed=True),
    svc: ValidationService = Depends(_get_service),
):
    """验证 Transformer 链路：Document → Transformer → Normalized Document。

    Request body (JSON)::

        {"file_path": "/data/test.pdf"}
    """
    return svc.validate_transformer(file_path)


# ---- Retrieval 验证路由 ----

@router.post("/retrieval/embedding", response_model=ValidationReport)
async def validate_embedding(
    svc: ValidationService = Depends(_get_service),
):
    """验证 Embedding 链路是否正常。

    验证 Embedding 模型是否能正常工作。
    """
    return svc.validate_embedding()


@router.post("/retrieval/vectorstore", response_model=ValidationReport)
async def validate_vectorstore(
    svc: ValidationService = Depends(_get_service),
):
    """验证 VectorStore 链路是否正常。

    验证向量存储是否能正常添加和搜索向量。
    """
    return svc.validate_vectorstore()


@router.post("/retrieval/search", response_model=ValidationReport)
async def validate_retrieval(
    svc: ValidationService = Depends(_get_service),
):
    """验证 Retrieval 链路是否正常。

    验证检索服务是否能正常返回相关结果。
    """
    return svc.validate_retrieval()


@router.post("/retrieval/rerank", response_model=ValidationReport)
async def validate_rerank(
    svc: ValidationService = Depends(_get_service),
):
    """验证 Rerank 链路是否正常。

    验证重排序服务是否能正常工作。
    """
    return svc.validate_rerank()
