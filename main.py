"""BestRAG 应用启动入口。

职责只限于：
- 创建 FastAPI 实例
- 初始化基础服务（WorkspaceManager → IngressService）
- 注册 Router
- 注入依赖

禁止在 main.py 中写入业务逻辑。
启动方式：uvicorn main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ingress.api.upload_api import (
    init_ingress_service,
    router as ingress_router,
)
from ingress.service.ingress_service import IngressService
from core.workspace_manager import WorkspaceManager
from document.dispatcher import DocumentDispatcher
from document.service import DocumentService
from processor.service import ProcessorService
from processor.chunker.service import ChunkService
from processor.transformer import TransformerService
from retrieval.embedding.service import EmbeddingService
from retrieval.vectorstore.service import VectorStoreService
from retrieval.retriever.service import RetrievalService
from retrieval.reranker.service import RerankService
from validation.api.validation_api import (
    init_validation_service,
    router as validation_router,
)
from validation.service import ValidationService

# 静态文件目录
STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例。

    初始化链：
        WorkspaceManager → IngressService → DocumentService → ProcessorService
            → RetrievalService → ValidationService → FastAPI Depends
    """
    # ---- 初始化基础服务 ----
    wm = WorkspaceManager()
    wm.init_all()

    ingress_service = IngressService(wm)

    # ---- FastAPI 应用 ----
    app = FastAPI(
        title="BestRAG",
        description="企业知识库 RAG 框架",
        version="0.1.0",
    )

    # ---- CORS ----
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- 初始化 DocumentService（Ingress → Document） ----
    document_dispatcher = DocumentDispatcher()
    document_service = DocumentService(document_dispatcher)

    # ---- 初始化 ProcessorService（Document → Clean Document） ----
    processor_service = ProcessorService()

    # ---- 初始化 ChunkService（Clean Document → Chunk[]） ----
    chunk_service = ChunkService()

    # ---- 初始化 TransformerService（Document → Normalized Document） ----
    transformer_service = TransformerService()

    # ---- 初始化 Retrieval 模块服务 ----
    embedding_service = EmbeddingService()
    vector_store_service = VectorStoreService()
    retrieval_service = RetrievalService(
        embedding_service=embedding_service,
        vector_store_service=vector_store_service
    )
    rerank_service = RerankService()

    # ---- 初始化 ValidationService ----
    validation_service = ValidationService(
        document_service, processor_service, chunk_service, transformer_service,
        embedding_service, vector_store_service, retrieval_service, rerank_service,
    )

    # ---- 注册路由 ----
    app.include_router(ingress_router)
    app.include_router(validation_router)

    # ---- 根路径重定向 → 前端 ----
    @app.get("/")
    async def root():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/static/index.html")

    # ---- favicon（避免 404 日志噪音） ----
    @app.get("/favicon.ico")
    async def favicon():
        from fastapi.responses import Response
        return Response(status_code=204)

    # ---- 注入依赖 ----
    init_ingress_service(ingress_service)
    init_validation_service(validation_service)

    return app


# 模块级实例（uvicorn 需要 "main:app"）
app = create_app()

# ---- 静态文件（mount 在 create_app 后避免被 include_router 影响） ----
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
