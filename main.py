"""BestRAG 应用启动入口。

职责只限于：
- 启动 Application Container
- 创建 FastAPI 实例
- 注册 Router
- 注入 API 依赖
"""

from pathlib import Path

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.application import bootstrap

STATIC_DIR = Path(__file__).parent / "static"

_app = bootstrap()
_app.start()

_ctx = _app.context
_ingress_service = _ctx.get_service("ingress")
_validation_service = _ctx.get_service("validation")


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例。"""
    app = FastAPI(title="BestRAG", description="企业知识库 RAG 框架", version="0.1.0")

    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    from ingress.api.upload_api import init_ingress_service, router as ingress_router
    from validation.api.validation_api import init_validation_service, router as validation_router

    app.include_router(ingress_router)
    app.include_router(validation_router)
    _register_feature_routes(app, _ctx)

    init_ingress_service(_ingress_service)
    init_validation_service(_validation_service)

    @app.get("/")
    async def root():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/static/console/index.html")

    @app.get("/favicon.ico")
    async def favicon():
        from fastapi.responses import Response
        return Response(status_code=204)

    return app


def _register_feature_routes(app: FastAPI, ctx) -> None:
    """注册 Feature Layer API 路由。"""
    from features.model import KnowledgeIngestRequest, QARequest

    kb_service = ctx.get_service("knowledge_base")
    qa_service = ctx.get_service("qa")

    feature_router = APIRouter(prefix="", tags=["features"])

    @feature_router.post("/knowledge/ingest")
    async def knowledge_ingest(request: KnowledgeIngestRequest):
        return kb_service.ingest(request)

    @feature_router.get("/knowledge/status")
    async def knowledge_status():
        return kb_service.status()

    @feature_router.post("/qa/ask")
    async def qa_ask(request: QARequest):
        return qa_service.ask(request)

    app.include_router(feature_router)


app = create_app()

if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
