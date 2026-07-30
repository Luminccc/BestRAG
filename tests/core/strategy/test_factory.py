"""StrategyFactory 单元测试。"""

import pytest

from core.registry import get_registry
from core.registry.center import reset_registry
from core.strategy.factory import StrategyFactory
from core.strategy.base import BaseStrategy


class _TestChunkStrategy(BaseStrategy):
    name: str = "test_chunk"
    def __init__(self, **kwargs):
        self.params = kwargs
    def execute(self, text, document_id):
        return [{"text": text, "id": document_id}]


class TestStrategyFactory:
    """StrategyFactory 功能测试。"""

    def setup_method(self):
        reset_registry()

    def _register_test_strategy(self, key, cls):
        get_registry().strategy.register(key, cls)

    def test_create_chunk_strategy(self):
        """从 Registry 创建 Chunk 策略。"""
        self._register_test_strategy("chunk:test", _TestChunkStrategy)
        factory = StrategyFactory()
        strategy = factory.create_chunk("test")
        assert isinstance(strategy, BaseStrategy)
        assert strategy.name == "test_chunk"

    def test_create_with_params(self):
        """创建策略时传递参数。"""
        self._register_test_strategy("chunk:test", _TestChunkStrategy)
        factory = StrategyFactory()
        strategy = factory.create_chunk("test", chunk_size=300, overlap=30)
        assert strategy.params["chunk_size"] == 300

    def test_create_unregistered_raises(self):
        """创建未注册的策略应抛出 KeyError。"""
        factory = StrategyFactory()
        with pytest.raises(KeyError):
            factory.create_chunk("non_existent")

    def test_create_methods_exist(self):
        """Factory 有三大创建方法。"""
        factory = StrategyFactory()
        assert hasattr(factory, "create_chunk")
        assert hasattr(factory, "create_retrieval")
        assert hasattr(factory, "create_fusion")
