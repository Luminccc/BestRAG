"""BaseSimilarityProvider — 相似度计算 Provider 抽象。

为 SemanticChunk 等策略提供文本相似度计算能力。

内置实现：
- JaccardSimilarityProvider：基于词重叠的 Jaccard 相似度
- CosineSimilarityProvider：基于向量余弦相似度
"""

from abc import abstractmethod
from typing import List

from core.provider.base import BaseProvider


class BaseSimilarityProvider(BaseProvider):
    """相似度计算 Provider 基类。"""

    name: str = "base_similarity"

    @abstractmethod
    def similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度。

        Args:
            text1: 第一段文本。
            text2: 第二段文本。

        Returns:
            [0, 1] 范围的相似度分数，越接近 1 越相似。
        """

    def execute(self, text1: str, text2: str) -> float:
        """委托给 similarity。"""
        return self.similarity(text1, text2)


class JaccardSimilarityProvider(BaseSimilarityProvider):
    """基于词重叠的 Jaccard 相似度。"""

    name: str = "jaccard"

    def similarity(self, text1: str, text2: str) -> float:
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union)


class CosineSimilarityProvider(BaseSimilarityProvider):
    """基于词频向量的余弦相似度（无需外部 Embedding 服务）。"""

    name: str = "cosine"

    def similarity(self, text1: str, text2: str) -> float:
        vec1 = self._word_vector(text1)
        vec2 = self._word_vector(text2)
        return self._cosine(vec1, vec2)

    def _word_vector(self, text: str) -> dict[str, float]:
        words = text.lower().split()
        vec: dict[str, float] = {}
        for w in words:
            vec[w] = vec.get(w, 0.0) + 1.0
        return vec

    def _cosine(self, a: dict[str, float], b: dict[str, float]) -> float:
        intersection = set(a) & set(b)
        dot = sum(a[k] * b.get(k, 0.0) for k in intersection)
        norm_a = sum(v * v for v in a.values()) ** 0.5
        norm_b = sum(v * v for v in b.values()) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
