"""BestRAG v0.3 Phase 0 测试 — Infrastructure Alignment。

覆盖：
1. Model 测试  — BaseModel 序列化
2. Service 测试 — BaseService 生命周期
3. Repository 测试 — CRUD 接口
4. Registry 测试 — ModelRegistry / RepositoryRegistry
5. Config 测试 — v0.3 新配置分区
6. Provider 测试 — BaseCacheProvider / BaseStorageProvider

运行::

    uv run pytest tests/core/v03/test_phase0.py -v
"""

import pytest
from datetime import datetime
from typing import Any, List, Optional

from core.models import BaseModel, Metadata
from core.service import BaseService
from core.repository import BaseRepository
from core.registry.model import ModelRegistry
from core.registry.repository import RepositoryRegistry
from core.registry.center import RegistryCenter, get_registry, reset_registry
from core.provider import BaseCacheProvider, BaseStorageProvider
from core.config import CoreConfig, get_config, ConfigManager
from core.config_models import TraceConfig, CacheConfig, StorageConfig


# ═══════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _reset_state():
    """每个测试前重置全局状态。"""
    ConfigManager().reset()
    reset_registry()
    yield
    ConfigManager().reset()
    reset_registry()


# ═══════════════════════════════════════════════════
# Test 1: Model 测试
# ═══════════════════════════════════════════════════

class _TestDoc(BaseModel):
    """测试用 Model。"""
    def __init__(self, title: str, content: str, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.content = content


def test_base_model_init():
    """BaseModel 初始化应有 id 和时间戳。"""
    doc = _TestDoc(title="t", content="c")
    assert doc.id is not None
    assert isinstance(doc.id, str)
    assert isinstance(doc.created_at, datetime)
    assert isinstance(doc.updated_at, datetime)
    assert doc.title == "t"
    assert doc.content == "c"


def test_base_model_to_dict():
    """to_dict 应正确序列化所有字段。"""
    doc = _TestDoc(title="hello", content="world")
    d = doc.to_dict()
    assert d["title"] == "hello"
    assert d["content"] == "world"
    assert "id" in d
    assert "created_at" in d
    assert "updated_at" in d
    # datetime 应转为 ISO 字符串
    assert isinstance(d["created_at"], str)


def test_base_model_to_json():
    """to_json 应输出合法 JSON。"""
    doc = _TestDoc(title="hello", content="world")
    import json
    obj = json.loads(doc.to_json())
    assert obj["title"] == "hello"
    assert obj["content"] == "world"


def test_base_model_custom_id():
    """支持外部传入 ID。"""
    doc = _TestDoc(id="my_id", title="t", content="c")
    assert doc.id == "my_id"


def test_metadata_defaults():
    """Metadata 默认值正确。"""
    m = Metadata()
    assert m.source is None
    assert m.tags == []
    assert m.extra == {}


def test_metadata_to_dict():
    """Metadata.to_dict 合并 source、tags 和 extra。"""
    m = Metadata(source="web", tags=["rag"], extra={"key": "val"})
    d = m.to_dict()
    assert d["source"] == "web"
    assert d["tags"] == ["rag"]
    assert d["key"] == "val"


# ═══════════════════════════════════════════════════
# Test 2: Service 测试
# ═══════════════════════════════════════════════════

class _TestService(BaseService):
    """测试用 Service。"""
    name = "test_service"

    def __init__(self):
        self.initialized = False
        self.closed = False

    def initialize(self):
        self.initialized = True

    def close(self):
        self.closed = True


def test_service_lifecycle():
    """Service 生命周期 initialize → close 正确。"""
    svc = _TestService()
    assert not svc.initialized
    assert not svc.closed

    svc.initialize()
    assert svc.initialized
    assert not svc.closed

    svc.close()
    assert svc.closed


def test_service_name():
    """Service 应有 name 属性。"""
    svc = _TestService()
    assert svc.name == "test_service"


# ═══════════════════════════════════════════════════
# Test 3: Repository 测试
# ═══════════════════════════════════════════════════

class _TestRepo(BaseRepository):
    """基于内存的测试 Repository。"""
    def __init__(self):
        self._store: dict[str, Any] = {}

    def save(self, obj: Any) -> Any:
        self._store[obj.id] = obj
        return obj

    def get(self, id: str) -> Optional[Any]:
        return self._store.get(id)

    def delete(self, id: str) -> bool:
        if id in self._store:
            del self._store[id]
            return True
        return False

    def list(self, **filters: Any) -> List[Any]:
        return list(self._store.values())


def test_repository_save_and_get():
    """save → get 应返回同一对象。"""
    repo = _TestRepo()
    doc = _TestDoc(title="t", content="c")
    repo.save(doc)

    result = repo.get(doc.id)
    assert result is doc
    assert result.title == "t"


def test_repository_get_not_found():
    """get 不存在的 ID 应返回 None。"""
    repo = _TestRepo()
    assert repo.get("nonexistent") is None


def test_repository_delete():
    """delete 后 get 应返回 None。"""
    repo = _TestRepo()
    doc = _TestDoc(title="t", content="c")
    repo.save(doc)

    assert repo.delete(doc.id) is True
    assert repo.get(doc.id) is None
    assert repo.delete(doc.id) is False  # 第二次删除返回 False


def test_repository_list():
    """list 应返回所有已保存对象。"""
    repo = _TestRepo()
    repo.save(_TestDoc(title="a", content="1"))
    repo.save(_TestDoc(title="b", content="2"))

    items = repo.list()
    assert len(items) == 2


# ═══════════════════════════════════════════════════
# Test 4: Registry 测试
# ═══════════════════════════════════════════════════

def test_model_registry_register_and_get():
    """ModelRegistry 注册和获取 Model 类。"""
    reg = ModelRegistry()
    reg.register("test_doc", _TestDoc)

    cls = reg.get("test_doc")
    assert cls is _TestDoc


def test_model_registry_not_found():
    """获取未注册的 Model 应抛出 KeyError。"""
    reg = ModelRegistry()
    with pytest.raises(KeyError, match="not_registered"):
        reg.get("not_registered")


def test_model_registry_has():
    """has 方法正确检测注册状态。"""
    reg = ModelRegistry()
    assert not reg.has("test_doc")
    reg.register("test_doc", _TestDoc)
    assert reg.has("test_doc")


def test_model_registry_list():
    """list 返回所有已注册的 Model 名称。"""
    reg = ModelRegistry()
    reg.register("a", _TestDoc)
    reg.register("b", _TestDoc)
    assert set(reg.list()) == {"a", "b"}


def test_repository_registry_register_and_get():
    """RepositoryRegistry 注册和获取实例。"""
    reg = RepositoryRegistry()
    repo = _TestRepo()
    reg.register("test", repo)

    result = reg.get("test")
    assert result is repo


def test_repository_registry_not_found():
    """获取未注册的 Repository 应抛出 KeyError。"""
    reg = RepositoryRegistry()
    with pytest.raises(KeyError):
        reg.get("nonexistent")


def test_registry_center_has_new_registries():
    """RegistryCenter 应包含 model 和 repository 注册表。"""
    rc = RegistryCenter()
    assert hasattr(rc, "model")
    assert hasattr(rc, "repository")

    # 验证可以使用
    rc.model.register("doc", _TestDoc)
    assert rc.model.has("doc")

    rc.repository.register("test", _TestRepo())
    assert rc.repository.has("test")

    rc.clear_all()
    assert not rc.model.has("doc")
    assert not rc.repository.has("test")


# ═══════════════════════════════════════════════════
# Test 5: Config 测试
# ═══════════════════════════════════════════════════

def test_core_config_has_v03_sections():
    """CoreConfig 应包含 v0.3 新分区。"""
    config = CoreConfig()
    assert hasattr(config, "trace")
    assert hasattr(config, "cache")
    assert hasattr(config, "storage")

    # 默认值正确
    assert config.trace.enabled is True
    assert config.trace.storage == "local"
    assert config.cache.provider == "memory"
    assert config.cache.ttl == 3600
    assert config.storage.provider == "local"
    assert config.storage.base_path == "./data"


def test_config_defaults():
    """TraceConfig / CacheConfig / StorageConfig 默认值。"""
    trace = TraceConfig()
    assert trace.enabled is True
    assert trace.storage == "local"

    cache = CacheConfig()
    assert cache.provider == "memory"
    assert cache.ttl == 3600

    storage = StorageConfig()
    assert storage.provider == "local"
    assert storage.base_path == "./data"


# ═══════════════════════════════════════════════════
# Test 6: Provider 测试
# ═══════════════════════════════════════════════════

class _MemoryCacheProvider(BaseCacheProvider):
    """基于内存的缓存 Provider（测试用）。"""
    name = "test_cache"

    def __init__(self):
        self._store: dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self._store.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self._store[key] = value

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def clear(self) -> None:
        self._store.clear()


def test_cache_provider():
    """Cache Provider 基本操作。"""
    cache = _MemoryCacheProvider()
    cache.set("k1", "v1")
    assert cache.get("k1") == "v1"
    assert cache.get("missing") is None

    cache.delete("k1")
    assert cache.get("k1") is None

    cache.set("k2", "v2")
    cache.clear()
    assert cache.get("k2") is None


class _LocalStorageProvider(BaseStorageProvider):
    """本地存储 Provider（测试用）。"""
    name = "test_storage"

    def __init__(self):
        self._store: dict[str, Any] = {}

    def save(self, path: str, data: Any) -> str:
        self._store[path] = data
        return path

    def load(self, path: str) -> Optional[Any]:
        return self._store.get(path)

    def delete(self, path: str) -> bool:
        return self._store.pop(path, None) is not None


def test_storage_provider():
    """Storage Provider 基本操作。"""
    store = _LocalStorageProvider()
    store.save("/path/to/doc", "content")
    assert store.load("/path/to/doc") == "content"
    assert store.load("/missing") is None

    store.delete("/path/to/doc")
    assert store.load("/path/to/doc") is None


# ═══════════════════════════════════════════════════
# Test 7: 向后兼容测试
# ═══════════════════════════════════════════════════

def test_registry_center_backward_compatible():
    """RegistryCenter v0.2 接口继续有效。"""
    rc = RegistryCenter()

    # service 注册
    rc.service.register("old_svc", "instance")
    assert rc.service.get("old_svc") == "instance"

    # strategy 注册
    rc.strategy.register("old_strategy", _TestDoc)
    assert rc.strategy.has("old_strategy")

    # provider 注册
    rc.provider.register("old_provider", "provider_instance")
    assert rc.provider.get("old_provider") == "provider_instance"

    # evaluator 注册
    rc.evaluator.register("old_evaluator", _TestDoc)
    assert rc.evaluator.has("old_evaluator")

    # clear_all 仍工作
    rc.clear_all()
    assert not rc.service.has("old_svc")
