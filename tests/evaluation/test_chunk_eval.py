"""Chunk Evaluation + Benchmark + Service 测试。"""

from processor.chunker.model import Chunk
from evaluation.chunk.evaluator import ChunkEvaluator, ChunkCoherenceEvaluator
from evaluation.benchmark.dataset import EvaluationDataset, EvalSample
from evaluation.benchmark.runner import BenchmarkRunner
from evaluation.service.evaluation_service import EvaluationService


class TestChunkEvaluator:
    """Chunk 评测测试。"""

    def test_empty_chunks(self):
        eval = ChunkEvaluator()
        metrics = eval.evaluate([])
        assert metrics[0].value == 0

    def test_chunk_metrics(self):
        chunks = [Chunk(document_id="d1", content="A" * 100, index=i) for i in range(3)]
        eval = ChunkEvaluator()
        metrics = eval.evaluate(chunks)
        names = {m.name for m in metrics}
        assert "chunk_count" in names
        assert "avg_chunk_size" in names
        assert metrics[0].value == 3

    def test_coherence(self):
        chunks = [Chunk(document_id="d1", content="Hello world. This is a test.", index=0)]
        eval = ChunkCoherenceEvaluator()
        metrics = eval.evaluate(chunks)
        assert len(metrics) == 1


class TestEvaluationDataset:
    """EvaluationDataset 测试。"""

    def test_empty_dataset(self):
        ds = EvaluationDataset("test")
        assert ds.size == 0

    def test_add_sample(self):
        ds = EvaluationDataset("test")
        ds.add_sample(EvalSample(query="how?", expected_ids={"doc1"}))
        assert ds.size == 1
        assert ds.samples[0].query == "how?"


class TestEvaluationService:
    """EvaluationService 测试。"""

    def test_evaluate_retrieval(self):
        from retrieval.retriever.model import RetrievalResult
        svc = EvaluationService()
        results = [RetrievalResult(chunk_id="a", score=1.0, content="text", metadata={})]
        metrics = svc.evaluate_retrieval(results, {"a"}, k=1)
        assert len(metrics) >= 4
