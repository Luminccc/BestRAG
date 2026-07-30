"""BestRAG v0.3 Phase 1 测试 — Knowledge Management Framework。

覆盖：
1. Model 测试     — KnowledgeBase / Document / DocumentVersion / IndexRecord
2. Repository 测试 — 三种 Repository 的 CRUD
3. Service 测试    — KnowledgeService / DocumentService / IndexService
4. Index 测试      — IndexPipelineManager 生命周期
5. Config 测试     — KnowledgeConfig / IndexConfig
6. Registry 测试   — 模块注册
7. 集成测试        — 完整知识库生命周期

运行::

    uv run pytest tests/core/v03/knowledge/ -v
"""

import pytest
from datetime import datetime
from typing import Any, List, Optional

from core.models import BaseModel
from core.models.knowledge import (
    KnowledgeBase,
    KnowledgeBaseStatus,
    Document,
    DocumentStatus,
    DocumentVersion,
    IndexRecord,
    IndexStatus,
)
from core.repository.knowledge import (
    KnowledgeBaseRepository,
    DocumentRepository,
    IndexRepository,
)
from core.service import BaseService
from core.config_models.knowledge import KnowledgeConfig, IndexConfig
from core.config import CoreConfig, ConfigManager
from core.registry.center import RegistryCenter, get_registry, reset_registry
from knowledge import (
    KnowledgeService,
    DocumentService,
    IndexService,
    IndexPipelineManager,
)
from knowledge.registry import register_knowledge_module


# ═══════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _reset_state():
    ConfigManager().reset()
    reset_registry()
    yield
    ConfigManager().reset()
    reset_registry()


# ═══════════════════════════════════════════════════
# Test 1: Model 测试
# ═══════════════════════════════════════════════════

class TestKnowledgeBaseModel:
    """KnowledgeBase 模型测试。"""

    def test_create_default(self):
        """创建知识库，默认状态为 CREATED。"""
        kb = KnowledgeBase(name="测试库")
        assert kb.id is not None
        assert kb.name == "测试库"
        assert kb.description == ""
        assert kb.config == {}
        assert kb.status == KnowledgeBaseStatus.CREATED
        assert isinstance(kb.created_at, datetime)

    def test_create_with_all_fields(self):
        """创建知识库，指定所有字段。"""
        kb = KnowledgeBase(
            name="技术文档",
            description="内部技术文档库",
            config={"chunk_strategy": "hierarchical"},
            status=KnowledgeBaseStatus.READY,
        )
        assert kb.name == "技术文档"
        assert kb.description == "内部技术文档库"
        assert kb.config["chunk_strategy"] == "hierarchical"
        assert kb.status == KnowledgeBaseStatus.READY

    def test_status_transition(self):
        """状态流转。"""
        kb = KnowledgeBase(name="test")
        assert kb.status == KnowledgeBaseStatus.CREATED
        kb.status = KnowledgeBaseStatus.BUILDING
        assert kb.status == KnowledgeBaseStatus.BUILDING
        kb.status = KnowledgeBaseStatus.READY
        assert kb.status == KnowledgeBaseStatus.READY
        kb.status = KnowledgeBaseStatus.FAILED
        assert kb.status == KnowledgeBaseStatus.FAILED

    def test_to_dict(self):
        """序列化包含枚举值转换。"""
        kb = KnowledgeBase(name="test", status=KnowledgeBaseStatus.READY)
        d = kb.to_dict()
        assert d["name"] == "test"
        assert d["status"] == "ready"  # 枚举转字符串

    def test_to_json(self):
        """JSON 序列化。"""
        kb = KnowledgeBase(name="test")
        import json
        obj = json.loads(kb.to_json())
        assert obj["name"] == "test"
        assert "id" in obj


class TestDocumentModel:
    """Document (v0.3) 模型测试。"""

    def test_create_default(self):
        """创建文档，默认状态为 PENDING。"""
        doc = Document(knowledge_base_id="kb_1")
        assert doc.knowledge_base_id == "kb_1"
        assert doc.content == ""
        assert doc.version == 1
        assert doc.status == DocumentStatus.PENDING

    def test_create_with_content(self):
        """创建带内容的文档。"""
        doc = Document(
            knowledge_base_id="kb_1",
            source="/path/to/file.pdf",
            content="文档内容",
            metadata={"author": "test"},
            status=DocumentStatus.READY,
        )
        assert doc.source == "/path/to/file.pdf"
        assert doc.content == "文档内容"
        assert doc.metadata["author"] == "test"
        assert doc.status == DocumentStatus.READY

    def test_version_increment(self):
        """版本号初始为 1。"""
        doc = Document(knowledge_base_id="kb_1", content="v1")
        assert doc.version == 1


class TestDocumentVersionModel:
    """DocumentVersion 模型测试。"""

    def test_create(self):
        """创建版本记录。"""
        ver = DocumentVersion(document_id="doc_1", version=1, content="abc")
        assert ver.document_id == "doc_1"
        assert ver.version == 1
        assert ver.content == "abc"

    def test_checksum(self):
        """校验和字段。"""
        ver = DocumentVersion(document_id="doc_1", checksum="abc123")
        assert ver.checksum == "abc123"


class TestIndexRecordModel:
    """IndexRecord 模型测试。"""

    def test_create_default(self):
        """默认状态为 PENDING。"""
        rec = IndexRecord(document_id="doc_1")
        assert rec.document_id == "doc_1"
        assert rec.status == IndexStatus.PENDING
        assert rec.chunk_count == 0

    def test_after_build(self):
        """构建完成后更新状态。"""
        rec = IndexRecord(
            document_id="doc_1",
            chunk_count=10,
            embedding_model="bge-m3",
            index_time=1.5,
            status=IndexStatus.READY,
        )
        assert rec.chunk_count == 10
        assert rec.embedding_model == "bge-m3"
        assert rec.index_time == 1.5
        assert rec.status == IndexStatus.READY


# ═══════════════════════════════════════════════════
# Test 2: Repository 测试
# ═══════════════════════════════════════════════════

class TestKnowledgeBaseRepository:
    """知识库仓库测试。"""

    def test_save_and_get(self):
        repo = KnowledgeBaseRepository()
        kb = KnowledgeBase(name="test")
        repo.save(kb)
        assert repo.get(kb.id) is kb

    def test_get_not_found(self):
        repo = KnowledgeBaseRepository()
        assert repo.get("nonexistent") is None

    def test_delete(self):
        repo = KnowledgeBaseRepository()
        kb = KnowledgeBase(name="test")
        repo.save(kb)
        assert repo.delete(kb.id) is True
        assert repo.get(kb.id) is None
        assert repo.delete(kb.id) is False

    def test_list_all(self):
        repo = KnowledgeBaseRepository()
        repo.save(KnowledgeBase(name="a"))
        repo.save(KnowledgeBase(name="b"))
        assert len(repo.list()) == 2

    def test_list_by_status(self):
        repo = KnowledgeBaseRepository()
        repo.save(KnowledgeBase(name="ready", status=KnowledgeBaseStatus.READY))
        repo.save(KnowledgeBase(name="building", status=KnowledgeBaseStatus.BUILDING))
        ready_list = repo.list(status=KnowledgeBaseStatus.READY)
        assert len(ready_list) == 1
        assert ready_list[0].name == "ready"


class TestDocumentRepository:
    """文档仓库测试。"""

    def test_save_and_get(self):
        repo = DocumentRepository()
        doc = Document(knowledge_base_id="kb_1", content="hello")
        repo.save(doc)
        assert repo.get(doc.id) is doc

    def test_list_by_kb(self):
        repo = DocumentRepository()
        repo.save(Document(knowledge_base_id="kb_1"))
        repo.save(Document(knowledge_base_id="kb_1"))
        repo.save(Document(knowledge_base_id="kb_2"))
        assert len(repo.list(knowledge_base_id="kb_1")) == 2
        assert len(repo.list(knowledge_base_id="kb_2")) == 1


class TestIndexRepository:
    """索引仓库测试。"""

    def test_find_by_document(self):
        repo = IndexRepository()
        r1 = IndexRecord(document_id="doc_1", status=IndexStatus.READY)
        r2 = IndexRecord(document_id="doc_1", status=IndexStatus.READY)
        repo.save(r1)
        repo.save(r2)
        found = repo.find_by_document("doc_1")
        assert found is not None

    def test_find_by_document_not_found(self):
        repo = IndexRepository()
        assert repo.find_by_document("nonexistent") is None


# ═══════════════════════════════════════════════════
# Test 3: Service 测试
# ═══════════════════════════════════════════════════

class TestKnowledgeService:
    """知识库服务测试。"""

    def test_create_knowledge_base(self):
        svc = KnowledgeService()
        kb = svc.create_knowledge_base("test", "description")
        assert kb.name == "test"
        assert kb.description == "description"
        assert kb.status == KnowledgeBaseStatus.CREATED

    def test_get_knowledge_base(self):
        svc = KnowledgeService()
        created = svc.create_knowledge_base("test")
        fetched = svc.get_knowledge_base(created.id)
        assert fetched is created

    def test_get_not_found(self):
        svc = KnowledgeService()
        assert svc.get_knowledge_base("nonexistent") is None

    def test_delete_knowledge_base(self):
        svc = KnowledgeService()
        kb = svc.create_knowledge_base("test")
        assert svc.delete_knowledge_base(kb.id) is True
        assert svc.get_knowledge_base(kb.id) is None

    def test_delete_not_found(self):
        svc = KnowledgeService()
        assert svc.delete_knowledge_base("nonexistent") is False

    def test_list_knowledge_bases(self):
        svc = KnowledgeService()
        svc.create_knowledge_base("a")
        svc.create_knowledge_base("b")
        assert len(svc.list_knowledge_bases()) == 2

    def test_update_status(self):
        svc = KnowledgeService()
        kb = svc.create_knowledge_base("test")
        svc.update_knowledge_base_status(kb.id, KnowledgeBaseStatus.READY)
        assert svc.get_knowledge_base(kb.id).status == KnowledgeBaseStatus.READY


class TestDocumentService:
    """文档管理服务测试。"""

    def test_add_document(self):
        svc = DocumentService()
        doc = svc.add_document("kb_1", "content", source="/path")
        assert doc.knowledge_base_id == "kb_1"
        assert doc.content == "content"
        assert doc.source == "/path"
        assert doc.status == DocumentStatus.READY
        assert doc.version == 1

    def test_get_document(self):
        svc = DocumentService()
        created = svc.add_document("kb_1", "hello")
        fetched = svc.get_document(created.id)
        assert fetched is created

    def test_delete_document(self):
        svc = DocumentService()
        doc = svc.add_document("kb_1", "content")
        assert svc.delete_document(doc.id) is True
        assert svc.get_document(doc.id) is None

    def test_list_documents(self):
        svc = DocumentService()
        svc.add_document("kb_1", "doc1")
        svc.add_document("kb_1", "doc2")
        svc.add_document("kb_2", "doc3")
        assert len(svc.list_documents("kb_1")) == 2

    def test_update_document_new_version(self):
        svc = DocumentService()
        doc = svc.add_document("kb_1", "v1")
        updated = svc.update_document(doc.id, "v2")
        assert updated is not None
        assert updated.version == 2
        assert updated.content == "v2"

    def test_update_document_no_change(self):
        svc = DocumentService()
        doc = svc.add_document("kb_1", "same content")
        updated = svc.update_document(doc.id, "same content")
        assert updated.version == 1  # 无变化，版本不变

    def test_version_history(self):
        svc = DocumentService()
        doc = svc.add_document("kb_1", "v1")
        svc.update_document(doc.id, "v2")
        svc.update_document(doc.id, "v3")
        versions = svc.get_document_versions(doc.id)
        assert len(versions) == 3
        assert versions[0].version == 1
        assert versions[2].version == 3


class TestIndexService:
    """索引管理服务测试。"""

    def test_build_index_default(self):
        """索引构建（使用默认空管线，返回成功）。"""
        svc = IndexService()
        doc = Document(knowledge_base_id="kb_1", content="test")
        record = svc.build_index(doc)
        assert record.status == IndexStatus.READY
        assert record.document_id == doc.id

    def test_rebuild_index(self):
        svc = IndexService()
        doc = Document(knowledge_base_id="kb_1", content="test")
        r1 = svc.build_index(doc)
        r2 = svc.rebuild_index(doc)
        assert r2.status == IndexStatus.READY
        # 旧记录应被清理
        old = svc.get_index_status(doc.id)
        assert old is not None

    def test_incremental_no_old_index(self):
        """无旧索引时增量更新等同于全量构建。"""
        svc = IndexService()
        doc = Document(knowledge_base_id="kb_1", content="test")
        record = svc.incremental_update(doc)
        assert record.status == IndexStatus.READY

    def test_incremental_with_old_index(self):
        """有旧索引时增量更新执行重建。"""
        svc = IndexService()
        doc = Document(knowledge_base_id="kb_1", content="test")
        svc.build_index(doc, "bge-m3")
        record = svc.incremental_update(doc, "bge-m3")
        assert record.status == IndexStatus.READY


# ═══════════════════════════════════════════════════
# Test 4: IndexPipelineManager 测试
# ═══════════════════════════════════════════════════

class TestIndexPipelineManager:
    """索引管线管理器测试。"""

    def test_build_with_chunk_func(self):
        """带切分函数的全量构建。"""
        mgr = IndexPipelineManager(
            chunk_func=lambda doc: [{"id": "c1", "content": "chunk1"}],
        )
        doc = type("Doc", (), {"id": "d1", "content": "test"})()
        count = mgr.build(doc)
        assert count == 1

    def test_build_empty_chunks(self):
        """切分结果为空时返回 0。"""
        mgr = IndexPipelineManager(
            chunk_func=lambda doc: [],
        )
        doc = type("Doc", (), {"id": "d1", "content": ""})()
        count = mgr.build(doc)
        assert count == 0

    def test_incremental_update(self):
        """增量更新。"""
        mgr = IndexPipelineManager()
        doc = type("Doc", (), {"id": "d1", "content": "test"})()
        count = mgr.incremental(doc, [{"id": "c1", "content": "changed"}])
        assert count == 1

    def test_incremental_empty(self):
        """无变更时增量更新返回 0。"""
        mgr = IndexPipelineManager()
        doc = type("Doc", (), {"id": "d1", "content": "test"})()
        count = mgr.incremental(doc, [])
        assert count == 0

    def test_rebuild(self):
        """重建等同于全量构建。"""
        mgr = IndexPipelineManager(
            chunk_func=lambda doc: [{"id": "c1", "content": "chunk1"}],
        )
        doc = type("Doc", (), {"id": "d1", "content": "test"})()
        assert mgr.rebuild(doc) == 1

    def test_full_pipeline(self):
        """完整管线：切分 → embedding → write。"""
        embed_called = []
        write_called = []

        def chunk_fn(doc):
            return [{"id": "c1", "content": "hello"}, {"id": "c2", "content": "world"}]

        def embed_fn(chunks):
            embed_called.append(True)
            return [[0.1, 0.2], [0.3, 0.4]]

        def write_fn(chunks, vectors):
            write_called.append(True)
            assert len(vectors) == 2

        mgr = IndexPipelineManager(
            chunk_func=chunk_fn,
            embed_func=embed_fn,
            write_func=write_fn,
        )
        doc = type("Doc", (), {"id": "d1", "content": "test"})()
        count = mgr.build(doc)
        assert count == 2
        assert embed_called == [True]
        assert write_called == [True]


# ═══════════════════════════════════════════════════
# Test 5: Config 测试
# ═══════════════════════════════════════════════════

def test_knowledge_config_defaults():
    """KnowledgeConfig 默认值。"""
    cfg = KnowledgeConfig()
    assert cfg.default_chunk_strategy == "hierarchical"
    assert cfg.auto_sync is False


def test_index_config_defaults():
    """IndexConfig 默认值。"""
    cfg = IndexConfig()
    assert cfg.auto_rebuild is True
    assert cfg.incremental is True
    assert cfg.embedding_model == "bge-m3"


def test_core_config_has_knowledge():
    """CoreConfig 包含 knowledge 和 index 分区。"""
    cfg = CoreConfig()
    assert hasattr(cfg, "knowledge")
    assert hasattr(cfg, "index")
    assert cfg.knowledge.default_chunk_strategy == "hierarchical"
    assert cfg.index.auto_rebuild is True


# ═══════════════════════════════════════════════════
# Test 6: Registry 测试
# ═══════════════════════════════════════════════════

def test_register_knowledge_module():
    """注册 Knowledge 模块到 RegistryCenter。"""
    register_knowledge_module()
    rc = get_registry()

    # Model 注册
    assert rc.model.has("KnowledgeBase")
    assert rc.model.has("Document")
    assert rc.model.has("DocumentVersion")
    assert rc.model.has("IndexRecord")

    # Repository 注册
    assert rc.repository.has("knowledge_base")
    assert rc.repository.has("document")
    assert rc.repository.has("index")

    # Service 注册
    assert rc.service.has("knowledge")
    assert rc.service.has("knowledge_document")
    assert rc.service.has("knowledge_index")


def test_registry_model_get():
    """通过 Registry 获取 Model 类。"""
    register_knowledge_module()
    rc = get_registry()
    cls = rc.model.get("KnowledgeBase")
    assert cls is KnowledgeBase


def test_registry_service_works():
    """通过 Registry 获取 Service 并调用的完整流程。"""
    register_knowledge_module()
    rc = get_registry()

    kb_svc = rc.service.get("knowledge")
    assert isinstance(kb_svc, KnowledgeService)

    kb = kb_svc.create_knowledge_base("registry_test")
    assert kb.name == "registry_test"


# ═══════════════════════════════════════════════════
# Test 7: 集成测试 — 完整知识库生命周期
# ═══════════════════════════════════════════════════

def test_full_knowledge_lifecycle():
    """完整集成：创建 KB → 添加文档 → 构建索引 → 查询状态。"""
    register_knowledge_module()
    rc = get_registry()

    # 1. 创建知识库
    kb_svc = rc.service.get("knowledge")
    kb = kb_svc.create_knowledge_base(
        name="集成测试库",
        description="集成测试",
        config={"chunk_strategy": "recursive"},
    )
    kb_svc.update_knowledge_base_status(kb.id, KnowledgeBaseStatus.READY)
    assert kb.status == KnowledgeBaseStatus.READY

    # 2. 添加文档
    doc_svc = rc.service.get("knowledge_document")
    doc = doc_svc.add_document(
        knowledge_base_id=kb.id,
        content="这是一篇测试文档的内容。BestRAG v0.3 知识库管理。",
        source="test.txt",
        metadata={"author": "tester"},
    )
    assert doc.knowledge_base_id == kb.id
    assert doc.version == 1

    # 3. 更新文档内容（版本递增）
    doc_svc.update_document(doc.id, "更新后的内容。v0.3 Knowledge Management。")
    assert doc_svc.get_document(doc.id).version == 2

    # 4. 构建索引
    idx_svc = rc.service.get("knowledge_index")
    record = idx_svc.build_index(doc, embedding_model="bge-m3")
    assert record.status == IndexStatus.READY
    assert record.document_id == doc.id

    # 5. 查询索引状态
    status = idx_svc.get_index_status(doc.id)
    assert status is not None
    assert status.status == IndexStatus.READY

    # 6. 重建索引
    record2 = idx_svc.rebuild_index(doc)
    assert record2.status == IndexStatus.READY

    # 7. 列出知识库
    kb_list = kb_svc.list_knowledge_bases()
    assert len(kb_list) >= 1

    # 8. 列出文档
    docs = doc_svc.list_documents(kb.id)
    assert len(docs) == 1

    # 9. 版本历史
    versions = doc_svc.get_document_versions(doc.id)
    assert len(versions) == 2

    # 10. 删除文档
    assert doc_svc.delete_document(doc.id) is True

    # 11. 删除知识库
    assert kb_svc.delete_knowledge_base(kb.id) is True


def test_model_registration_from_core():
    """核心模型可通过 core.models.knowledge 访问。"""
    from core.models.knowledge import KnowledgeBase, Document, DocumentVersion, IndexRecord
    assert KnowledgeBase is not None
    assert Document is not None
    assert DocumentVersion is not None
    assert IndexRecord is not None
