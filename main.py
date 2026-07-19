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

from knowledge_base.ingress.api.upload_api import (
    init_ingress_service,
    router as ingress_router,
)
from knowledge_base.ingress.service.ingress_service import IngressService
from knowledge_base.workspace_manager import WorkspaceManager

# 静态文件目录
STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例。

    初始化链：
        WorkspaceManager → IngressService → FastAPI Depends
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

    # ---- 注册路由 ----
    app.include_router(ingress_router)

    # ---- 根路径重定向 → 前端 ----
    @app.get("/")
    async def root():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/static/index.html")

    # ---- 注入依赖 ----
    init_ingress_service(ingress_service)

    return app


# 模块级实例（uvicorn 需要 "main:app"）
app = create_app()

# ---- 静态文件（mount 在 create_app 后避免被 include_router 影响） ----
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
