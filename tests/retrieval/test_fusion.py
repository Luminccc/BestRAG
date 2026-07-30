"""Fusion 策略单元测试。"""

import pytest

from core.strategy.fusion.base import BaseFusionStrategy
from core.strategy.fusion.weighted import WeightedFusionStrategy
from core.strategy.fusion.rrf import RRFFusionStrategy
from retrieval.retriever.model import RetrievalResult


def _make_result(chunk_id: str, score: float) -> RetrievalResult:
    return RetrievalResult(chunk_id=chunk_id, score=score, content="text", metadata={})


class TestBaseFusionStrategy:
    """BaseFusionStrategy 接口测试。"""

    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            BaseFusionStrategy()  # type: ignore


class TestWeightedFusionStrategy:
    """加权融合测试。"""

    def test_fuse_two_lists(self):
        strategy = WeightedFusionStrategy()
        list_a = [_make_result("a", 0.9), _make_result("b", 0.7)]
        list_b = [_make_result("b", 0.8), _make_result("c", 0.6)]
        results = strategy.fuse([list_a, list_b])
        assert len(results) == 3
        assert results[0].chunk_id == "b"  # 0.7 + 0.8 = 1.5

    def test_single_list(self):
        strategy = WeightedFusionStrategy()
        results = strategy.fuse([[_make_result("a", 1.0)]])
        assert len(results) == 1


class TestRRFFusionStrategy:
    """RRF 融合测试。"""

    def test_fuse_two_lists(self):
        strategy = RRFFusionStrategy(k=60)
        list_a = [_make_result("a", 0.9), _make_result("b", 0.8)]
        list_b = [_make_result("b", 0.7), _make_result("c", 0.6)]
        results = strategy.fuse([list_a, list_b])
        assert len(results) == 3

    def test_rank_based_scoring(self):
        strategy = RRFFusionStrategy(k=10)
        list_a = [_make_result("x", 1.0), _make_result("y", 0.5)]
        results = strategy.fuse([list_a])
        assert results[0].chunk_id == "x"
        assert results[0].score > results[1].score

    def test_name(self):
        assert RRFFusionStrategy().name == "rrf"
