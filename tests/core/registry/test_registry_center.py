"""RegistryCenter 单元测试。"""

from core.registry.center import RegistryCenter, get_registry, reset_registry
from core.registry.service import ServiceRegistry
from core.registry.strategy import StrategyRegistry
from core.registry.provider import ProviderRegistry
from core.registry.evaluator import EvaluatorRegistry


class TestRegistryCenter:
    """RegistryCenter 聚合功能测试。"""

    def setup_method(self):
        reset_registry()

    def test_center_holds_four_registries(self):
        """RegistryCenter 包含四类注册表。"""
        rc = RegistryCenter()
        assert isinstance(rc.service, ServiceRegistry)
        assert isinstance(rc.strategy, StrategyRegistry)
        assert isinstance(rc.provider, ProviderRegistry)
        assert isinstance(rc.evaluator, EvaluatorRegistry)

    def test_clear_all(self):
        """clear_all 清空所有注册表。"""
        rc = RegistryCenter()
        rc.service.register("svc", 1)
        rc.strategy.register("strat", dict)
        rc.provider.register("prov", "p")
        rc.evaluator.register("eval", list)
        rc.clear_all()
        assert rc.service.has("svc") is False
        assert rc.strategy.has("strat") is False
        assert rc.provider.has("prov") is False
        assert rc.evaluator.has("eval") is False

    def test_get_registry_singleton(self):
        """get_registry() 返回同一实例。"""
        reset_registry()
        rc1 = get_registry()
        rc2 = get_registry()
        assert rc1 is rc2

    def test_registry_integration(self):
        """各 Registry 协同工作。"""
        rc = RegistryCenter()

        # 注册服务
        rc.service.register("doc_service", {"type": "document"})
        rc.service.register("retrieval_service", {"type": "retrieval"})

        # 注册策略
        rc.strategy.register("recursive", dict)
        rc.strategy.register("semantic", list)

        # 验证
        assert rc.service.has("doc_service")
        assert rc.service.get("doc_service") == {"type": "document"}
        assert rc.strategy.get("recursive") is dict
        assert rc.strategy.has("semantic")
