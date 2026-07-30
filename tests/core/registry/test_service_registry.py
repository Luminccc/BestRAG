"""ServiceRegistry 单元测试。

验证：
- register / get / has / remove / clear 基础操作
- register_factory 延迟创建
- 未找到时抛出 ServiceNotFoundError
"""

import pytest

from core.exception import ServiceNotFoundError
from core.registry.service import ServiceRegistry


@pytest.fixture
def registry():
    """每个测试一个干净的 ServiceRegistry 实例。"""
    return ServiceRegistry()


class TestServiceRegistry:
    """ServiceRegistry 基础操作测试。"""

    def test_register_and_get(self, registry: ServiceRegistry):
        """注册服务实例后可获取。"""
        registry.register("test_svc", {"name": "test"})
        result = registry.get("test_svc")
        assert result == {"name": "test"}

    def test_get_not_found(self, registry: ServiceRegistry):
        """获取未注册的服务应抛出异常。"""
        with pytest.raises(ServiceNotFoundError):
            registry.get("non_existent")

    def test_has(self, registry: ServiceRegistry):
        """检查服务是否已注册。"""
        registry.register("svc_a", "value_a")
        assert registry.has("svc_a") is True
        assert registry.has("svc_b") is False

    def test_remove(self, registry: ServiceRegistry):
        """移除后不可再获取。"""
        registry.register("tmp", "to_remove")
        registry.remove("tmp")
        assert registry.has("tmp") is False

    def test_unregister_compat(self, registry: ServiceRegistry):
        """unregister（v0.1 兼容名）功能正常。"""
        registry.register("tmp", "val")
        registry.unregister("tmp")
        assert registry.has("tmp") is False

    def test_clear(self, registry: ServiceRegistry):
        """清空所有注册。"""
        registry.register("a", 1)
        registry.register("b", 2)
        registry.clear()
        assert registry.has("a") is False
        assert registry.has("b") is False

    def test_register_overwrites_factory(self, registry: ServiceRegistry):
        """注册实例会覆盖同名的工厂。"""
        registry.register_factory("svc", lambda: "from_factory")
        registry.register("svc", "direct_instance")
        assert registry.get("svc") == "direct_instance"

    def test_factory_lazy_creation(self, registry: ServiceRegistry):
        """工厂函数在首次 get 时执行并缓存结果。"""
        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return {"count": call_count}

        registry.register_factory("lazy", factory)
        # 首次 get 应执行工厂
        result1 = registry.get("lazy")
        assert result1["count"] == 1
        # 再次 get 应返回缓存结果（工厂不再执行）
        result2 = registry.get("lazy")
        assert result2["count"] == 1

    def test_list(self, registry: ServiceRegistry):
        """列出已注册名称。"""
        registry.register("a", 1)
        registry.register("b", 2)
        names = registry.list()
        assert "a" in names
        assert "b" in names
