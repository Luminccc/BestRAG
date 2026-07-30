"""Evaluation Core 单元测试。"""

import pytest

from evaluation.core.evaluator import BaseEvaluator
from evaluation.core.metric import MetricResult
from evaluation.core.result import EvaluationReport


class TestBaseEvaluator:
    """BaseEvaluator 接口测试。"""
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            BaseEvaluator()  # type: ignore


class TestMetricResult:
    """MetricResult 测试。"""
    def test_defaults(self):
        m = MetricResult()
        assert m.name == ""
        assert m.value == 0.0

    def test_with_values(self):
        m = MetricResult(name="recall@5", value=0.85, metadata={"k": 5})
        assert m.name == "recall@5"
        assert m.value == 0.85


class TestEvaluationReport:
    """EvaluationReport 测试。"""
    def test_empty_report(self):
        r = EvaluationReport()
        assert r.to_dict()["scenario"] == ""

    def test_to_dict(self):
        r = EvaluationReport(
            scenario="tech_docs",
            strategy_profile={"chunk": "recursive"},
            metrics=[MetricResult(name="recall@5", value=0.9)],
        )
        d = r.to_dict()
        assert d["scenario"] == "tech_docs"
        assert d["strategy_profile"]["chunk"] == "recursive"
        assert d["metrics"][0]["value"] == 0.9

    def test_get_metric(self):
        r = EvaluationReport(metrics=[
            MetricResult(name="recall@5", value=0.85),
            MetricResult(name="mrr", value=0.72),
        ])
        assert r.get_metric("recall@5") == 0.85
        assert r.get_metric("nonexistent") == 0.0
