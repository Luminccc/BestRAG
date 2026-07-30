"""BaseStrategy 单元测试。"""

import pytest

from core.strategy.base import BaseStrategy


class _ConcreteStrategy(BaseStrategy):
    """最小可用策略实现。"""
    name: str = "concrete"

    def execute(self, *args, **kwargs):
        return "executed"


class TestBaseStrategy:
    """BaseStrategy 接口测试。"""

    def test_abstract_class_cannot_be_instantiated(self):
        """BaseStrategy 是抽象类，不能直接实例化。"""
        with pytest.raises(TypeError):
            BaseStrategy()  # type: ignore

    def test_concrete_strategy_can_be_instantiated(self):
        """实现 execute 后可实例化。"""
        s = _ConcreteStrategy()
        assert s.name == "concrete"

    def test_execute_returns_result(self):
        """execute 返回策略执行结果。"""
        s = _ConcreteStrategy()
        assert s.execute() == "executed"

    def test_default_lifecycle_methods(self):
        """initialize 和 close 有默认空实现。"""
        s = _ConcreteStrategy()
        s.initialize()  # 不应抛出异常
        s.close()       # 不应抛出异常

    def test_name_default_is_empty(self):
        """未设置 name 应保持空字符串。"""
        class NoNameStrategy(BaseStrategy):
            def execute(self, *args, **kwargs):
                return None

        s = NoNameStrategy()
        assert s.name == ""
