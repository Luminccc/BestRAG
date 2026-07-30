"""DocumentService — 知识库文档管理服务。

负责文档的上传、更新、删除和版本管理。
"""

from hashlib import md5
from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.models.knowledge import Document, DocumentStatus, DocumentVersion
from core.repository.knowledge import DocumentRepository
from core.service import BaseService

logger = get_logger("knowledge.document")


class DocumentService(BaseService):
    """文档管理服务。

    Usage::

        svc = DocumentService(doc_repo)
        doc = svc.add_document(kb_id, content="...")
        doc = svc.update_document(doc_id, content="new version")
        versions = svc.get_document_versions(doc_id)
    """

    name = "knowledge_document"

    def __init__(self, doc_repo: Optional[DocumentRepository] = None):
        self._doc_repo = doc_repo or DocumentRepository()
        # 简易版本存储（生产环境应使用独立版本仓库）
        self._versions: Dict[str, list] = {}

    def initialize(self) -> None:
        """初始化文档服务。"""
        logger.info("DocumentService 初始化完成")

    def close(self) -> None:
        """释放资源。"""
        logger.info("DocumentService 已关闭")

    # ── 文档 CRUD ─────────────────────────────────

    def add_document(
        self,
        knowledge_base_id: str,
        content: str,
        source: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """添加文档到知识库。"""
        doc = Document(
            knowledge_base_id=knowledge_base_id,
            source=source,
            content=content,
            metadata=metadata or {},
            status=DocumentStatus.READY,
        )
        self._doc_repo.save(doc)

        # 创建初始版本
        self._create_version(doc.id, doc.content, doc.version)
        logger.info(f"文档添加成功: {doc.id} -> KB:{knowledge_base_id}")
        return doc

    def get_document(self, doc_id: str) -> Optional[Document]:
        """获取文档。"""
        return self._doc_repo.get(doc_id)

    def delete_document(self, doc_id: str) -> bool:
        """删除文档。"""
        result = self._doc_repo.delete(doc_id)
        if result:
            self._versions.pop(doc_id, None)
            logger.info(f"文档已删除: {doc_id}")
        return result

    def list_documents(
        self, knowledge_base_id: str
    ) -> List[Document]:
        """列出知识库下的所有文档。"""
        return self._doc_repo.list(knowledge_base_id=knowledge_base_id)

    # ── 文档更新 ─────────────────────────────────

    def update_document(self, doc_id: str, content: str) -> Optional[Document]:
        """更新文档内容（自动创建新版本）。"""
        doc = self._doc_repo.get(doc_id)
        if doc is None:
            return None

        old_checksum = md5(doc.content.encode()).hexdigest()
        new_checksum = md5(content.encode()).hexdigest()

        # 内容无变化则跳过
        if old_checksum == new_checksum:
            logger.info(f"文档内容无变化: {doc_id}")
            return doc

        doc.content = content
        doc.version += 1
        doc.status = DocumentStatus.READY
        self._doc_repo.save(doc)
        self._create_version(doc.id, content, doc.version)

        logger.info(f"文档已更新: {doc_id} -> v{doc.version}")
        return doc

    # ── 版本管理 ─────────────────────────────────

    def get_document_versions(self, doc_id: str) -> List[DocumentVersion]:
        """获取文档的所有版本历史。"""
        return list(self._versions.get(doc_id, []))

    def _create_version(self, doc_id: str, content: str, version: int) -> DocumentVersion:
        """创建文档版本记录。"""
        checksum = md5(content.encode()).hexdigest()
        ver = DocumentVersion(
            document_id=doc_id,
            version=version,
            content=content,
            checksum=checksum,
        )
        if doc_id not in self._versions:
            self._versions[doc_id] = []
        self._versions[doc_id].append(ver)
        return ver
