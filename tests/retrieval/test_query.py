"""Query Rewrite 策略测试。"""

from core.strategy.query import (
    BaseQueryRewriteStrategy,
    SimpleQueryRewriteStrategy,
)
from core.strategy.query.rewrite import LLMQueryRewriteStrategy


class TestBaseQueryRewrite:
    """BaseQueryRewriteStrategy 测试。"""

    def test_abstract_cannot_instantiate(self):
        import pytest
        with pytest.raises(TypeError):
            BaseQueryRewriteStrategy()  # type: ignore

    def test_simple_rewrite(self):
        strategy = SimpleQueryRewriteStrategy()
        result = strategy.rewrite("How to use milvus?")
        assert "Milvus" in result or "milvus" in result

    def test_simple_rewrite_keeps_original(self):
        strategy = SimpleQueryRewriteStrategy()
        result = strategy.rewrite("unknown term xyz")
        assert "unknown term xyz" in result

    def test_llm_rewrite_fallback(self):
        """无 LLMProvider 时返回原查询。"""
        strategy = LLMQueryRewriteStrategy()
        result = strategy.rewrite("test query")
        assert result == "test query"

    def test_execute_delegates(self):
        strategy = SimpleQueryRewriteStrategy()
        assert strategy.execute("milvus") == strategy.rewrite("milvus")
