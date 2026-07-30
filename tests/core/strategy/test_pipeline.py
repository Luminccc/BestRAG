"""StrategyPipeline 单元测试。"""

import pytest

from core.strategy.base import BaseStrategy
from core.strategy.pipeline import StrategyPipeline


class _Double(BaseStrategy):
    name: str = "double"
    def execute(self, value):
        return value * 2


class _AddOne(BaseStrategy):
    name: str = "add_one"
    def execute(self, value):
        return value + 1


class TestStrategyPipeline:
    """StrategyPipeline 功能测试。"""

    def test_pipeline_executes_in_order(self):
        """策略按顺序执行，输出传递给下一个。"""
        pipe = StrategyPipeline([_AddOne(), _Double()])
        result = pipe.execute(5)
        # add_one(5) = 6, double(6) = 12
        assert result == 12

    def test_pipeline_empty_raises(self):
        """空策略列表应抛出 ValueError。"""
        with pytest.raises(ValueError):
            StrategyPipeline([])

    def test_pipeline_with_single_strategy(self):
        """单个策略的 Pipeline 正确执行。"""
        pipe = StrategyPipeline([_Double()])
        assert pipe.execute(3) == 6

    def test_pipeline_length(self):
        """__len__ 返回策略数量。"""
        pipe = StrategyPipeline([_AddOne(), _Double()])
        assert len(pipe) == 2

    def test_pipeline_repr(self):
        """__repr__ 展示策略链。"""
        pipe = StrategyPipeline([_AddOne(), _Double()])
        assert "add_one" in repr(pipe)
        assert "double" in repr(pipe)

    def test_pipeline_reuses_strategies(self):
        """同一策略实例可在多个 Pipeline 中使用。"""
        add = _AddOne()
        p1 = StrategyPipeline([add])
        p2 = StrategyPipeline([add])
        assert p1.execute(1) == 2
        assert p2.execute(10) == 11
