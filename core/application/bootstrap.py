"""Bootstrap — 应用组装入口。

负责：
1. 加载配置
2. 创建 ApplicationContext
3. 初始化 Workspace + ResourceManager
4. 创建所有 Domain Service
5. 组装 Application

不负责：
- 业务逻辑
- FastAPI 创建
- 路由注册
"""

from core.application.context import ApplicationContext
from core.config import get_config
from core.logger import get_logger
from core.registry.center import RegistryCenter
from core.resource_manager import ResourceManager
from core.workspace_manager import WorkspaceManager

# Domain Services
from document.dispatcher import DocumentDispatcher
from document.service import DocumentService
from processor.service import ProcessorService
from processor.chunker.service import ChunkService
from processor.transformer import TransformerService
from retrieval.embedding.service import EmbeddingService
from retrieval.vectorstore.service import VectorStoreService
from retrieval.retriever.service import RetrievalService
from retrieval.reranker.service import RerankService
from generation.service import GenerationService
from validation.service import ValidationService
from ingress.service.ingress_service import IngressService

logger = get_logger("bestrag.bootstrap")


def bootstrap() -> "Application":
    """组装完整应用运行时。

    流程：
        Config → Context → Workspace → ResourceManager → Services → Application

    Returns:
        已初始化但未 start 的 Application 实例。
    """
    logger.info("Bootstrap 开始...")

    # ── Step 1: 配置 ──
    config = get_config()
    logger.info(f"配置加载完成: {config.app.name} v{config.app.version}")

    # ── Step 2: 创建 RegistryCenter（后续 Provider/Service/Strategy 在此注册）──
    registry_center = RegistryCenter()
    logger.info("RegistryCenter 初始化完成 (Service/Strategy/Provider/Evaluator/Model/Repository)")

    # ── Step 3: 创建 Context ──
    ctx = ApplicationContext()
    ctx.config = config
    ctx.registry = registry_center

    # ── Step 4: Workspace ──
    wm = WorkspaceManager()
    wm.init_all()
    ctx.workspace_manager = wm
    logger.info("Workspace 初始化完成")

    # ── Step 5: ResourceManager ──
    rm = ResourceManager()
    ctx.resource_manager = rm

    # ── Step 6: IngressService ──
    ingress_service = IngressService(wm)
    ctx.services["ingress"] = ingress_service
    registry_center.service.register("ingress", ingress_service)

    # ── Step 7: DocumentService ──
    document_dispatcher = DocumentDispatcher()
    document_service = DocumentService(document_dispatcher)
    ctx.services["document"] = document_service
    registry_center.service.register("document", document_service)

    # ── Step 8: Processor Services ──
    processor_service = ProcessorService()
    chunk_service = ChunkService()
    transformer_service = TransformerService()
    ctx.services["processor"] = processor_service
    ctx.services["chunker"] = chunk_service
    ctx.services["transformer"] = transformer_service
    registry_center.service.register("processor", processor_service)
    registry_center.service.register("chunker", chunk_service)
    registry_center.service.register("transformer", transformer_service)

    # ── Step 9: Retrieval Services ──
    embedding_service = EmbeddingService()
    vector_store_service = VectorStoreService()
    retrieval_service = RetrievalService(
        embedding_service=embedding_service,
        vector_store_service=vector_store_service,
    )
    rerank_service = RerankService()
    ctx.services["embedding"] = embedding_service
    ctx.services["vectorstore"] = vector_store_service
    ctx.services["retrieval"] = retrieval_service
    ctx.services["reranker"] = rerank_service
    registry_center.service.register("embedding", embedding_service)
    registry_center.service.register("vectorstore", vector_store_service)
    registry_center.service.register("retrieval", retrieval_service)
    registry_center.service.register("reranker", rerank_service)

    # ── Step 10: GenerationService ──
    generation_service = GenerationService()
    ctx.services["generation"] = generation_service
    registry_center.service.register("generation", generation_service)

    # ── Step 11: ValidationService ──
    validation_service = ValidationService(
        document_service=document_service,
        processor_service=processor_service,
        chunk_service=chunk_service,
        transformer_service=transformer_service,
        embedding_service=embedding_service,
        vector_store_service=vector_store_service,
        retrieval_service=retrieval_service,
        rerank_service=rerank_service,
        generation_service=generation_service,
    )
    ctx.services["validation"] = validation_service
    registry_center.service.register("validation", validation_service)

    # ── Step 12: Feature Services ──
    from indexing.service import IndexingService
    from features.knowledge_base import KnowledgeBaseService
    from features.qa import QAService

    indexing_service = IndexingService()
    ctx.services["indexing"] = indexing_service
    registry_center.service.register("indexing", indexing_service)

    kb_service = KnowledgeBaseService(
        ingress_service=ingress_service,
        document_service=document_service,
        processor_service=processor_service,
        indexing_service=indexing_service,
    )
    ctx.services["knowledge_base"] = kb_service
    registry_center.service.register("knowledge_base", kb_service)

    qa_service = QAService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
        rerank_service=rerank_service,
    )
    ctx.services["qa"] = qa_service
    registry_center.service.register("qa", qa_service)

    # ── Step 13: 组装 Application ──
    from core.application.application import Application
    app = Application(ctx)
    logger.info("Bootstrap 完成")

    return app
