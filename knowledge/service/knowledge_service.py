"""KnowledgeService — 知识库管理服务。

负责知识库的创建、删除、查询等生命周期管理。
"""

from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.models.knowledge import KnowledgeBase, KnowledgeBaseStatus
from core.repository.knowledge import KnowledgeBaseRepository
from core.service import BaseService

logger = get_logger("knowledge.service")


class KnowledgeService(BaseService):
    """知识库服务。

    Usage::

        svc = KnowledgeService(kb_repo)
        kb = svc.create_knowledge_base("技术文档", "内部文档库")
        kb_list = svc.list_knowledge_bases()
    """

    name = "knowledge"

    def __init__(self, kb_repo: Optional[KnowledgeBaseRepository] = None):
        self._kb_repo = kb_repo or KnowledgeBaseRepository()

    def initialize(self) -> None:
        """初始化知识库服务。"""
        logger.info("KnowledgeService 初始化完成")

    def close(self) -> None:
        """释放资源。"""
        logger.info("KnowledgeService 已关闭")

    # ── 核心接口 ──────────────────────────────────

    def create_knowledge_base(
        self,
        name: str,
        description: str = "",
        config: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeBase:
        """创建知识库。"""
        kb = KnowledgeBase(
            name=name,
            description=description,
            config=config or {},
            status=KnowledgeBaseStatus.CREATED,
        )
        self._kb_repo.save(kb)
        logger.info(f"知识库创建成功: {kb.id} - {name}")
        return kb

    def get_knowledge_base(self, kb_id: str) -> Optional[KnowledgeBase]:
        """获取知识库。"""
        return self._kb_repo.get(kb_id)

    def delete_knowledge_base(self, kb_id: str) -> bool:
        """删除知识库。"""
        kb = self._kb_repo.get(kb_id)
        if kb is None:
            logger.warning(f"知识库不存在: {kb_id}")
            return False
        self._kb_repo.delete(kb_id)
        logger.info(f"知识库已删除: {kb_id}")
        return True

    def list_knowledge_bases(
        self, status: Optional[KnowledgeBaseStatus] = None
    ) -> List[KnowledgeBase]:
        """列出知识库，可按状态过滤。"""
        filters = {}
        if status:
            filters["status"] = status
        return self._kb_repo.list(**filters)

    def update_knowledge_base_status(
        self, kb_id: str, status: KnowledgeBaseStatus
    ) -> Optional[KnowledgeBase]:
        """更新知识库状态。"""
        kb = self._kb_repo.get(kb_id)
        if kb is None:
            return None
        kb.status = status
        self._kb_repo.update(kb)
        return kb
