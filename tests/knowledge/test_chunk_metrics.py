"""Chunk 质量指标测试。"""

from processor.chunker.model import Chunk
from validation.metrics import ChunkQualityMetrics


class TestChunkQualityMetrics:
    """ChunkQualityMetrics 测试。"""

    def test_empty_chunks(self):
        metrics = ChunkQualityMetrics([])
        result = metrics.compute()
        assert result["error"] == "empty_chunks"
        assert result["chunk_count"] == 0

    def test_single_chunk(self):
        chunks = [
            Chunk(document_id="doc1", content="Hello world.", index=0, metadata={"strategy": "fixed"}),
        ]
        metrics = ChunkQualityMetrics(chunks)
        result = metrics.compute()
        assert result["chunk_count"] == 1
        assert result["size"]["average_token_length"] == 12  # len("Hello world.")
        assert result["size"]["min_length"] == 12
        assert result["size"]["max_length"] == 12

    def test_multiple_chunks_distribution(self):
        chunks = [
            Chunk(document_id="doc1", content="Short.", index=0),
            Chunk(document_id="doc1", content="A longer chunk of text here.", index=1),
            Chunk(document_id="doc1", content="Medium length text.", index=2),
        ]
        metrics = ChunkQualityMetrics(chunks)
        result = metrics.compute()
        assert result["chunk_count"] == 3
        assert result["distribution"]["length_variance"] > 0

    def test_structure_metrics_with_headings(self):
        chunks = [
            Chunk(document_id="doc1", content="Content", index=0,
                  metadata={"strategy": "heading", "heading": "Intro"}),
            Chunk(document_id="doc1", content="Content", index=1,
                  metadata={"strategy": "heading", "heading": "Details"}),
            Chunk(document_id="doc1", content="Content", index=2,
                  metadata={"strategy": "fixed"}),
        ]
        metrics = ChunkQualityMetrics(chunks)
        result = metrics.compute()
        assert result["structure"]["heading_preservation"] == 2
        assert result["structure"]["heading_ratio"] == 2 / 3

    def test_strategy_distribution(self):
        chunks = [
            Chunk(document_id="doc1", content="A", index=0, metadata={"strategy": "fixed"}),
            Chunk(document_id="doc1", content="B", index=1, metadata={"strategy": "fixed"}),
            Chunk(document_id="doc1", content="C", index=2, metadata={"strategy": "semantic"}),
        ]
        metrics = ChunkQualityMetrics(chunks)
        result = metrics.compute()
        assert result["structure"]["strategy_distribution"]["fixed"] == 2
        assert result["structure"]["strategy_distribution"]["semantic"] == 1
