"""StrategyRegistry 单元测试。"""

import pytest

from core.registry.strategy import StrategyRegistry


class TestStrategyRegistry:
    """StrategyRegistry 基础功能测试。"""

    @pytest.fixture
    def registry(self):
        return StrategyRegistry()

    def test_register_and_get(self, registry: StrategyRegistry):
        """注册策略类后可获取。"""
        registry.register("recursive", dict)
        cls = registry.get("recursive")
        assert cls is dict

    def test_get_not_found(self, registry: StrategyRegistry):
        """获取未注册的策略应抛出 KeyError。"""
        with pytest.raises(KeyError):
            registry.get("non_existent")

    def test_has(self, registry: StrategyRegistry):
        """检查策略是否已注册。"""
        registry.register("semantic", list)
        assert registry.has("semantic") is True
        assert registry.has("heading") is False

    def test_remove(self, registry: StrategyRegistry):
        """移除后不可再获取。"""
        registry.register("tmp", str)
        registry.remove("tmp")
        assert registry.has("tmp") is False

    def test_clear(self, registry: StrategyRegistry):
        """清空所有策略注册。"""
        registry.register("a", dict)
        registry.register("b", list)
        registry.clear()
        assert registry.has("a") is False
        assert registry.has("b") is False

    def test_list(self, registry: StrategyRegistry):
        """列出所有已注册的策略名。"""
        registry.register("fixed", str)
        registry.register("recursive", list)
        names = registry.list()
        assert "fixed" in names
        assert "recursive" in names
        assert len(names) == 2

    def test_register_overwrite(self, registry: StrategyRegistry):
        """同名注册应覆盖旧策略。"""
        registry.register("dup", str)
        registry.register("dup", list)
        assert registry.get("dup") is list
