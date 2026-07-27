"""Validation API — FastAPI 验证入口。

提供：
- POST /validation/document             单文件验证
- POST /validation/document/all         全量回归验证
- POST /validation/processor/cleaner    Cleaner 验证
- POST /validation/retrieval/embedding  Embedding 验证
- POST /validation/retrieval/vectorstore VectorStore 验证
- POST /validation/retrieval/search     Retrieval 验证
- POST /validation/retrieval/rerank     Rerank 验证
- GET  /validation/status               系统状态检查（V2）
- POST /validation/run                  执行全链路验证（V2）
- POST /validation/chat                 RAG 问答测试（V2）
"""

from typing import Optional

from fastapi import APIRouter, Body, Depends

from validation.model import ValidationReport, ChatResult, StatusResult, ScenarioResult, DebugResult
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


# ══════════════════════════════════════════════════════════
# V2: Generation / System / Chat 验证路由
# ══════════════════════════════════════════════════════════

@router.get("/status", response_model=StatusResult)
async def get_system_status(
    svc: ValidationService = Depends(_get_service),
):
    """获取系统各组件状态快照。

    Returns::

        {
            "core": "ok",
            "retrieval": "ok",
            "generation": "ok",
            "details": { ... }
        }
    """
    return svc.get_system_status()


@router.post("/run", response_model=ValidationReport)
async def run_validation(
    svc: ValidationService = Depends(_get_service),
):
    """执行全链路验证。

    验证 LLM / Generation / Embedding / VectorStore / Retrieval。
    LLM 相关检查需设置环境变量 BESTRAG_VALIDATION_LLM=true 才会实际调用 API。

    Returns::

        {
            "status": "success",
            "checks": [ ... ],
            "summary": { "pass": 3, "fail": 0, "skip": 2 }
        }
    """
    return svc.run_full_validation()


@router.post("/chat", response_model=ChatResult)
async def chat_test(
    query: str = Body(..., embed=True),
    use_test_data: bool = Body(False, embed=True),
    svc: ValidationService = Depends(_get_service),
):
    """RAG 问答测试。

    输入用户问题，返回检索结果 + LLM 答案 + 耗时信息。

    Request body (JSON)::

        {
            "query": "如何部署系统?",
            "use_test_data": false
        }

    Returns::

        {
            "answer": "...",
            "sources": [ ... ],
            "retrieval_time": 45.2,
            "generation_time": 1200.5,
            "total_time": 1245.7
        }
    """
    return svc.run_chat_test(query=query, use_test_data=use_test_data)


# ══════════════════════════════════════════════════════════
# V2 Enhancement: Scenario + Diagnostics 验证路由
# ══════════════════════════════════════════════════════════

@router.post("/scenario/knowledge-base", response_model=ScenarioResult)
async def scenario_knowledge_base(
    svc: ValidationService = Depends(_get_service),
):
    """Knowledge Base 场景验证。

    验证：文档创建 → 摄入 → 索引 → 状态更新。
    """
    return svc.validate_knowledge_base_scenario()


@router.post("/scenario/qa", response_model=ScenarioResult)
async def scenario_qa(
    svc: ValidationService = Depends(_get_service),
):
    """QA 场景验证。

    验证：提问 → 检索 → 生成 → 回答。
    """
    return svc.validate_qa_scenario()


@router.post("/scenario/rag-e2e", response_model=ScenarioResult)
async def scenario_rag_e2e(
    svc: ValidationService = Depends(_get_service),
):
    """RAG E2E 场景验证。

    验证完整闭环：文档 → 索引 → 问答 → 内容正确性。
    """
    return svc.validate_rag_e2e_scenario()


@router.post("/debug/retrieval", response_model=DebugResult)
async def debug_retrieval(
    query: str = Body(..., embed=True),
    svc: ValidationService = Depends(_get_service),
):
    """检索诊断。

    返回检索各阶段详情，用于 Debug 检索质量问题。

    Request body (JSON)::

        {"query": "如何安装？"}
    """
    return svc.debug_retrieval(query)


@router.post("/debug/generation", response_model=DebugResult)
async def debug_generation(
    query: str = Body(..., embed=True),
    svc: ValidationService = Depends(_get_service),
):
    """生成诊断。

    返回生成各阶段详情（Context / Prompt / LLM），用于 Debug 回答质量问题。

    Request body (JSON)::

        {"query": "如何安装？"}
    """
    return svc.debug_generation(query)
