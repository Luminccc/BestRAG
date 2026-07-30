"""ProfileRegistry + RankingEngine + Selector 测试。"""

from optimization.profile.model import RAGProfile
from optimization.profile.registry import ProfileRegistry
from optimization.optimizer.ranking import RankingEngine
from optimization.optimizer.selector import ProfileSelector
from optimization.experiment.experiment import Experiment
from evaluation.core.result import EvaluationReport
from evaluation.core.metric import MetricResult


class TestProfileRegistry:
    """ProfileRegistry 测试。"""

    def test_default_profiles_registered(self):
        reg = ProfileRegistry()
        names = reg.list_names()
        assert "default" in names
        assert "technical_doc" in names
        assert "faq" in names

    def test_register_custom(self):
        reg = ProfileRegistry()
        p = RAGProfile(name="my_profile", chunk_strategy="semantic")
        reg.register(p)
        assert reg.get("my_profile") is p

    def test_get_nonexistent(self):
        reg = ProfileRegistry()
        assert reg.get("nonexistent") is None

    def test_remove(self):
        reg = ProfileRegistry()
        p = RAGProfile(name="temp")
        reg.register(p)
        reg.remove("temp")
        assert reg.get("temp") is None


class TestRankingEngine:
    """RankingEngine 测试。"""

    def _make_experiment(self, name: str, recall: float, mrr: float, precision: float) -> Experiment:
        report = EvaluationReport(
            metrics=[
                MetricResult(name="recall@5", value=recall),
                MetricResult(name="mrr", value=mrr),
                MetricResult(name="precision@5", value=precision),
            ]
        )
        return Experiment(name=name, result=report)

    def test_rank_orders_by_score(self):
        a = self._make_experiment("A", 0.9, 0.8, 0.7)
        b = self._make_experiment("B", 0.7, 0.6, 0.5)
        engine = RankingEngine()
        ranked = engine.rank([b, a])
        assert ranked[0][0].name == "A"
        assert ranked[0][1] > ranked[1][1]

    def test_empty_experiments(self):
        engine = RankingEngine()
        ranked = engine.rank([])
        assert ranked == []

    def test_best_experiment(self):
        a = self._make_experiment("A", 0.9, 0.8, 0.7)
        b = self._make_experiment("B", 0.5, 0.5, 0.5)
        best, score = RankingEngine().get_best([a, b])
        assert best.name == "A"


class TestProfileSelector:
    """ProfileSelector 测试。"""

    def test_select_by_scenario(self):
        reg = ProfileRegistry()
        selector = ProfileSelector(reg)
        p = selector.select_by_scenario("technical")
        assert p.name == "technical_doc"

    def test_select_by_scenario_fallback(self):
        reg = ProfileRegistry()
        selector = ProfileSelector(reg)
        p = selector.select_by_scenario("unknown")
        assert p.name == "default"

    def test_select_for_knowledge_base_faq(self):
        reg = ProfileRegistry()
        selector = ProfileSelector(reg)
        p = selector.select_for_knowledge_base({"type": "faq"})
        assert p.name == "faq"

    def test_select_for_knowledge_base_technical(self):
        reg = ProfileRegistry()
        selector = ProfileSelector(reg)
        p = selector.select_for_knowledge_base({"type": "technical", "structure": "markdown"})
        assert p.name == "technical_doc"

    def test_select_for_knowledge_base_default(self):
        reg = ProfileRegistry()
        selector = ProfileSelector(reg)
        p = selector.select_for_knowledge_base({"type": "unknown"})
        assert p.name in [pr.name for pr in reg.list()]
