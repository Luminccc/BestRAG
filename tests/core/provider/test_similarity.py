"""SimilarityProvider 测试。"""

import math

import pytest

from core.provider import JaccardSimilarityProvider, CosineSimilarityProvider


class TestJaccardSimilarityProvider:
    """Jaccard 相似度测试。"""

    @staticmethod
    def provider():
        return JaccardSimilarityProvider()

    def test_name(self):
        assert self.provider().name == "jaccard"

    def test_identical_texts(self):
        sim = self.provider().similarity("hello world", "hello world")
        assert math.isclose(sim, 1.0)

    def test_partial_overlap(self):
        sim = self.provider().similarity("cat dog bird", "cat dog fish")
        assert 0.0 < sim < 1.0

    def test_no_overlap(self):
        sim = self.provider().similarity("aaa bbb", "ccc ddd")
        assert sim == 0.0

    def test_empty_text(self):
        sim = self.provider().similarity("", "hello")
        assert sim == 0.0


class TestCosineSimilarityProvider:
    """余弦相似度测试。"""

    @staticmethod
    def provider():
        return CosineSimilarityProvider()

    def test_name(self):
        assert self.provider().name == "cosine"

    def test_identical_texts(self):
        sim = self.provider().similarity("hello world", "hello world")
        assert math.isclose(sim, 1.0)

    def test_partial_overlap(self):
        sim = self.provider().similarity("cat dog bird", "cat dog fish")
        assert 0.0 < sim < 1.0

    def test_no_overlap(self):
        sim = self.provider().similarity("one two", "three four")
        assert sim == 0.0

    def test_empty_text(self):
        sim = self.provider().similarity("", "text")
        assert sim == 0.0
