"""ContextBuilder 测试。"""

from retrieval.context.builder import ContextBuilder
from retrieval.retriever.model import RetrievalResult


class TestContextBuilder:
    """ContextBuilder 测试。"""

    def _make_result(self, cid: str, content: str, score: float = 1.0, **meta) -> RetrievalResult:
        return RetrievalResult(chunk_id=cid, score=score, content=content, metadata=meta)

    def test_empty_results(self):
        builder = ContextBuilder()
        assert builder.build([]) == ""

    def test_single_result(self):
        builder = ContextBuilder()
        results = [self._make_result("c1", "Hello world")]
        context = builder.build(results)
        assert "Hello world" in context

    def test_multiple_results(self):
        builder = ContextBuilder()
        results = [
            self._make_result("c1", "First chunk"),
            self._make_result("c2", "Second chunk"),
        ]
        context = builder.build(results)
        assert "First chunk" in context
        assert "Second chunk" in context

    def test_metadata_in_context(self):
        builder = ContextBuilder()
        results = [self._make_result("c1", "Content", heading="Intro", source="test.md")]
        context = builder.build(results, include_metadata=True)
        assert "heading=Intro" in context or "Intro" in context

    def test_token_limit(self):
        builder = ContextBuilder(max_tokens=10)  # ~20 chars
        results = [
            self._make_result("c1", "A" * 50),
            self._make_result("c2", "B" * 50),
        ]
        context = builder.build(results)
        assert len(context) < 100  # 应被截断

    def test_deduplication(self):
        builder = ContextBuilder()
        results = [
            self._make_result("c1", "Duplicate text"),
            self._make_result("c1", "Duplicate text"),
        ]
        context = builder.build(results)
        assert context.count("Duplicate text") == 1

    def test_build_with_sources(self):
        builder = ContextBuilder()
        results = [self._make_result("c1", "Content", score=0.95)]
        context, sources = builder.build_with_sources(results)
        assert "Content" in context
        assert sources[0]["chunk_id"] == "c1"
        assert sources[0]["score"] == 0.95
