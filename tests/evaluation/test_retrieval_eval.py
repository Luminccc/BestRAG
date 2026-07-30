"""Retrieval Evaluation 单元测试。"""

from evaluation.retrieval.evaluator import RetrievalEvaluator
from retrieval.retriever.model import RetrievalResult


def _result(chunk_id: str, content: str = "") -> RetrievalResult:
    return RetrievalResult(chunk_id=chunk_id, score=1.0, content=content or chunk_id, metadata={})


class TestRetrievalEvaluator:
    """检索评测指标测试。"""

    @staticmethod
    def evaluator():
        return RetrievalEvaluator()

    def test_recall_all_hit(self):
        results = [_result("a"), _result("b"), _result("c")]
        metrics = self.evaluator().evaluate(results, {"a", "b"}, k=3)
        recall = [m for m in metrics if m.name == "recall@3"][0]
        assert recall.value == 1.0

    def test_recall_partial(self):
        results = [_result("a"), _result("x"), _result("y")]
        metrics = self.evaluator().evaluate(results, {"a", "b"}, k=3)
        recall = [m for m in metrics if m.name == "recall@3"][0]
        assert recall.value == 0.5

    def test_precision(self):
        results = [_result("a"), _result("b"), _result("c")]
        metrics = self.evaluator().evaluate(results, {"a", "b"}, k=3)
        prec = [m for m in metrics if m.name == "precision@3"][0]
        assert prec.value == 2 / 3

    def test_precision_empty_expected(self):
        results = [_result("a")]
        metrics = self.evaluator().evaluate(results, set(), k=1)
        prec = [m for m in metrics if m.name == "precision@1"][0]
        assert prec.value == 0.0

    def test_mrr_first_rank(self):
        results = [_result("a"), _result("b")]
        metrics = self.evaluator().evaluate(results, {"a"}, k=2)
        mrr = [m for m in metrics if m.name == "mrr"][0]
        assert mrr.value == 1.0

    def test_mrr_second_rank(self):
        results = [_result("x"), _result("b"), _result("c")]
        metrics = self.evaluator().evaluate(results, {"b"}, k=3)
        mrr = [m for m in metrics if m.name == "mrr"][0]
        assert mrr.value == 0.5

    def test_mrr_no_match(self):
        results = [_result("x"), _result("y")]
        metrics = self.evaluator().evaluate(results, {"z"}, k=2)
        mrr = [m for m in metrics if m.name == "mrr"][0]
        assert mrr.value == 0.0

    def test_ndcg(self):
        results = [_result("a"), _result("b"), _result("c")]
        metrics = self.evaluator().evaluate(results, {"a", "c"}, k=3)
        ndcg = [m for m in metrics if m.name == "ndcg@3"][0]
        assert 0.0 < ndcg.value <= 1.0

    def test_all_metrics_present(self):
        results = [_result("a")]
        metrics = self.evaluator().evaluate(results, {"a"}, k=1)
        names = {m.name for m in metrics}
        assert "recall@1" in names
        assert "precision@1" in names
        assert "mrr" in names
        assert "ndcg@1" in names
