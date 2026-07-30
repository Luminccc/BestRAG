"""Quality Metrics — 检索质量指标（v0.3 Phase 3 新增）。

- HitRate     : 命中率
- Diversity   : 多样性评分
- Coverage    : 知识库覆盖评分
"""

from typing import Any, Dict, List, Set

from evaluation.metric.base import BaseMetric


class HitRateMetric(BaseMetric):
    """HitRate — 命中率。

    判断检索结果是否命中目标文档。
    """

    def name(self) -> str:
        return "hit_rate"

    def calculate(
        self,
        retrieved: List[str],
        expected: Set[str],
        **kwargs: Any,
    ) -> float:
        if not expected:
            return 0.0
        return 1.0 if any(doc_id in expected for doc_id in retrieved) else 0.0


class DiversityScore(BaseMetric):
    """Diversity Score — 多样性评分。

    检测检索结果是否过度集中于某个来源。
    值越接近 1.0 表示来源越分散（多样性好）。
    """

    def name(self) -> str:
        return "diversity"

    def calculate(
        self,
        retrieved: List[str],
        source_fn=None,
        **kwargs: Any,
    ) -> float:
        if not retrieved:
            return 0.0
        if source_fn is None:
            # 默认：假设每个文档来自独立来源 → 最大多样性
            return 1.0
        sources = [source_fn(doc_id) for doc_id in retrieved]
        unique_sources = len(set(sources))
        return unique_sources / len(retrieved)


class CoverageScore(BaseMetric):
    """Coverage Score — 知识库覆盖评分。

    检测检索结果覆盖了多少不同的知识领域。
    """

    def name(self) -> str:
        return "coverage"

    def calculate(
        self,
        retrieved: List[str],
        total_categories: int = 1,
        category_fn=None,
        **kwargs: Any,
    ) -> float:
        if not retrieved or total_categories == 0:
            return 0.0
        if category_fn is None:
            return 1.0
        categories = {category_fn(doc_id) for doc_id in retrieved}
        return len(categories) / total_categories
