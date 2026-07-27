"""Core Integration Test — 验证 Core Runtime 满足 PDR v1.0 验收标准。

运行方式::

    uv run pytest tests/test_core_integration.py -v
"""

import pytest

from core.app import Application
from core.config import CoreConfig, get_config, ConfigManager
from core.exception import ServiceNotFoundError
from core.provider import BaseProvider
from core.registry import (
    ServiceRegistry,
    register_service,
    register_service_factory,
    get_service,
    unregister_service,
)


# ═══════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _reset_config():
    """每个测试前重置配置状态。"""
    ConfigManager().reset()
    yield
    ConfigManager().reset()


@pytest.fixture(autouse=True)
def _reset_registry():
    """每个测试前清空注册中心。"""
    registry = ServiceRegistry()
    registry.clear()
    yield
    registry.clear()


# ═══════════════════════════════════════════════════
# TC-001: Application Lifecycle
# ═══════════════════════════════════════════════════

def test_application_lifecycle():
    """Application.start() → is_running → Application.stop() 无异常。"""
    app = Application()

    assert not app.is_running, "启动前 is_running 应为 False"

    app.start()
    assert app.is_running, "启动后 is_running 应为 True"

    app.stop()
    assert not app.is_running, "关闭后 is_running 应为 False"


# ═══════════════════════════════════════════════════
# TC-002: Registry Service Management
# ═══════════════════════════════════════════════════

class _FakeService:
    """测试用服务。"""
    pass


def test_registry_register_and_get():
    """register_service → get_service 返回同一实例。"""
    svc = _FakeService()
    register_service("test_svc", svc)

    result = get_service("test_svc")
    assert result is svc, "get_service 应返回注册时的同一实例"

    # factory 注册并懒加载
    register_service_factory("lazy_svc", _FakeService)
    lazy_result = get_service("lazy_svc")
    assert isinstance(lazy_result, _FakeService)


def test_registry_not_found():
    """获取未注册的服务应抛出 ServiceNotFoundError。"""
    with pytest.raises(ServiceNotFoundError, match="not_found"):
        get_service("not_found")


def test_registry_has_and_unregister():
    """has / unregister 行为正确。"""
    registry = ServiceRegistry()
    registry.register("svc", _FakeService())

    assert registry.has("svc")
    registry.unregister("svc")
    assert not registry.has("svc")


# ═══════════════════════════════════════════════════
# TC-003: Resource Singleton
# ═══════════════════════════════════════════════════

class _HeavyService:
    """模拟重量级资源。"""
    def __init__(self):
        self.name = "heavy"


def test_resource_singleton():
    """factory 注册后，多次 get_service 返回同一实例（懒加载缓存）。"""
    call_count = 0

    def factory():
        nonlocal call_count
        call_count += 1
        return _HeavyService()

    register_service_factory("heavy", factory)

    r1 = get_service("heavy")
    r2 = get_service("heavy")

    assert r1 is r2, "多次 get 应返回同一实例（Singleton）"
    assert call_count == 1, "工厂函数应只调用一次"


# ═══════════════════════════════════════════════════
# TC-004: Provider Lifecycle
# ═══════════════════════════════════════════════════

class _TestProvider(BaseProvider):
    """模拟 Provider，记录 initialize / close 调用。"""
    def __init__(self):
        self.initialized = False
        self.closed = False

    def initialize(self) -> None:
        self.initialized = True

    def close(self) -> None:
        self.closed = True


def test_provider_initialize():
    """initialize() 设置 initialized=True。"""
    p = _TestProvider()
    assert not p.initialized
    p.initialize()
    assert p.initialized


def test_provider_close():
    """close() 设置 closed=True。"""
    p = _TestProvider()
    p.initialize()
    assert not p.closed
    p.close()
    assert p.closed


# ═══════════════════════════════════════════════════
# TC-005: Config Loading
# ═══════════════════════════════════════════════════

def test_config_structure():
    """get_config() 返回包含所需分区的 CoreConfig。"""
    config = get_config()

    # app
    assert config.app.name == "BestRAG"
    assert hasattr(config.app, "version")
    assert hasattr(config.app, "debug")

    # embedding
    assert config.embedding.provider == "bge"
    assert config.embedding.dim == 1024
    assert hasattr(config.embedding, "model_name")
    assert hasattr(config.embedding, "api_url")

    # vectorstore
    assert config.vectorstore.provider == "milvus"
    assert config.vectorstore.host == "127.0.0.1"
    assert config.vectorstore.port == 19530

    # reranker
    assert config.reranker.provider == "bge"
    assert hasattr(config.reranker, "model_name")
    assert hasattr(config.reranker, "api_url")

    # retrieval
    assert config.retrieval.top_k == 10

    # workspace
    assert config.workspace.root == "./workspace"
    assert hasattr(config.workspace, "upload")
    assert hasattr(config.workspace, "logs")


def test_config_singleton():
    """多次调用 get_config() 返回同一实例。"""
    c1 = get_config()
    c2 = get_config()
    assert c1 is c2
