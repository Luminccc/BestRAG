"""knowledge.registry — 知识库模块注册初始化。

负责将 Knowledge 模块的 Model / Repository / Service 注册到全局 RegistryCenter。

使用示例::

    from core.registry import get_registry
    from knowledge.registry import register_knowledge_module

    register_knowledge_module()
    rc = get_registry()
    rc.model.get("KnowledgeBase")
"""

from core.logger import get_logger
from core.models.knowledge import (
    KnowledgeBase,
    Document,
    DocumentVersion,
    IndexRecord,
)
from core.registry import get_registry
from core.repository.knowledge import (
    KnowledgeBaseRepository,
    DocumentRepository,
    IndexRepository,
)
from knowledge.service import (
    KnowledgeService,
    DocumentService,
    IndexService,
)

logger = get_logger("knowledge.registry")


def register_knowledge_module() -> None:
    """注册 Knowledge 模块全部组件到全局 RegistryCenter。

    注册内容：
    1. Model      — KnowledgeBase / Document / DocumentVersion / IndexRecord
    2. Repository — KnowledgeBaseRepository / DocumentRepository / IndexRepository
    3. Service    — KnowledgeService / DocumentService / IndexService
    """
    rc = get_registry()

    # ── 1. 注册 Model 类 ──
    rc.model.register("KnowledgeBase", KnowledgeBase)
    rc.model.register("Document", Document)
    rc.model.register("DocumentVersion", DocumentVersion)
    rc.model.register("IndexRecord", IndexRecord)
    logger.info("Knowledge Model 注册完成")

    # ── 2. 注册 Repository 实例 ──
    kb_repo = KnowledgeBaseRepository()
    doc_repo = DocumentRepository()
    idx_repo = IndexRepository()

    rc.repository.register("knowledge_base", kb_repo)
    rc.repository.register("document", doc_repo)
    rc.repository.register("index", idx_repo)
    logger.info("Knowledge Repository 注册完成")

    # ── 3. 注册 Service 实例 ──
    kb_svc = KnowledgeService(kb_repo)
    doc_svc = DocumentService(doc_repo)
    idx_svc = IndexService(idx_repo)

    rc.service.register("knowledge", kb_svc)
    rc.service.register("knowledge_document", doc_svc)
    rc.service.register("knowledge_index", idx_svc)
    logger.info("Knowledge Service 注册完成")
