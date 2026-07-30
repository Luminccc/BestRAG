"""Retrieval / Fusion 策略接口单元测试。"""

import pytest

from core.strategy import BaseRetrievalStrategy, BaseFusionStrategy


class TestRetrievalStrategy:
    """Retrieval 策略接口测试。"""

    def test_base_is_abstract(self):
        """BaseRetrievalStrategy 不能直接实例化。"""
        with pytest.raises(TypeError):
            BaseRetrievalStrategy()  # type: ignore

    def test_concrete_retrieval_strategy(self):
        """实现 retrieve 后可实例化。"""
        class VectorRetrieval(BaseRetrievalStrategy):
            name: str = "vector"
            def retrieve(self, query, top_k=10, **kwargs):
                return [{"query": query, "score": 0.95}]

        s = VectorRetrieval()
        assert s.name == "vector"
        results = s.retrieve("test")
        assert len(results) == 1

    def test_execute_delegates_to_retrieve(self):
        """execute 委托给 retrieve。"""
        class TestRetrieval(BaseRetrievalStrategy):
            name: str = "test"
            def retrieve(self, query, top_k=10, **kwargs):
                return [query]

        s = TestRetrieval()
        assert s.execute("hello") == s.retrieve("hello")


class TestFusionStrategy:
    """Fusion 策略接口测试。"""

    def test_base_is_abstract(self):
        """BaseFusionStrategy 不能直接实例化。"""
        with pytest.raises(TypeError):
            BaseFusionStrategy()  # type: ignore

    def test_concrete_fusion_strategy(self):
        """实现 fuse 后可实例化。"""
        class RRFFusion(BaseFusionStrategy):
            name: str = "rrf"
            def fuse(self, results, **kwargs):
                return [r for sublist in results for r in sublist]

        s = RRFFusion()
        assert s.name == "rrf"
        result = s.fuse([[1, 2], [3, 4]])
        assert result == [1, 2, 3, 4]

    def test_execute_delegates_to_fuse(self):
        """execute 委托给 fuse。"""
        class TestFusion(BaseFusionStrategy):
            name: str = "test"
            def fuse(self, results, **kwargs):
                return sum(results, [])

        s = TestFusion()
        assert s.execute([[1], [2]]) == s.fuse([[1], [2]])
