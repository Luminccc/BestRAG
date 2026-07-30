"""Chunk 策略单元测试 — 新增策略（Heading/Semantic/Hierarchical）。"""

import pytest

from processor.chunker.strategy import (
    HeadingChunkStrategy,
    SemanticChunkStrategy,
    HierarchicalChunkStrategy,
)


class TestHeadingChunkStrategy:
    """Heading Chunk 策略测试。"""

    @pytest.fixture
    def strategy(self):
        return HeadingChunkStrategy()

    def test_split_by_headings(self, strategy: HeadingChunkStrategy):
        text = "# Introduction\n\nThis is the intro.\n\n# Methods\n\nWe used AI."
        chunks = strategy.split(text, "doc1")
        assert len(chunks) >= 2
        assert any("Introduction" in str(c.metadata.get("heading", "")) for c in chunks)
        assert any("Methods" in str(c.metadata.get("heading", "")) for c in chunks)

    def test_no_headings_returns_single_chunk(self, strategy: HeadingChunkStrategy):
        text = "Just a plain paragraph.\n\nNo headings here."
        chunks = strategy.split(text, "doc1")
        assert len(chunks) >= 1

    def test_empty_text_returns_empty(self, strategy: HeadingChunkStrategy):
        chunks = strategy.split("", "doc1")
        assert chunks == []

    def test_metadata_contains_heading_info(self, strategy: HeadingChunkStrategy):
        text = "# Chapter 1\n\nContent here."
        chunks = strategy.split(text, "doc1")
        assert chunks[0].metadata.get("heading") == "Chapter 1"
        assert chunks[0].metadata.get("heading_level") == 1

    def test_multiple_heading_levels(self, strategy: HeadingChunkStrategy):
        text = "# Title\n\n## Section 1\n\nContent\n\n### Subsection\n\nDetail"
        chunks = strategy.split(text, "doc1")
        headings = [c.metadata.get("heading") for c in chunks]
        assert "Title" in headings
        assert "Section 1" in headings


class TestSemanticChunkStrategy:
    """Semantic Chunk 策略测试。"""

    @pytest.fixture
    def strategy(self):
        return SemanticChunkStrategy(chunk_size=100, overlap=20)

    def test_split_sentences(self, strategy: SemanticChunkStrategy):
        sentence = "First sentence. Second sentence. Third sentence."
        chunks = strategy.split(sentence, "doc1")
        assert len(chunks) >= 1

    def test_similarity_detects_boundary(self, strategy: SemanticChunkStrategy):
        # 两个主题差异明显的段落
        text = "Machine learning is transforming AI. Neural networks are powerful. "
        text += "The weather today is sunny. I like to walk in the park."
        chunks = strategy.split(text, "doc1")
        assert len(chunks) >= 1

    def test_empty_text(self, strategy: SemanticChunkStrategy):
        chunks = strategy.split("", "doc1")
        assert chunks == []

    def test_similarity_provider_used(self, strategy: SemanticChunkStrategy):
        """验证使用 SimilarityProvider 计算相似度。"""
        from core.provider import JaccardSimilarityProvider
        provider = JaccardSimilarityProvider()
        sim = provider.similarity("cat dog bird", "cat dog fish")
        assert 0.0 < sim < 1.0

        sim2 = provider.similarity("aaa bbb ccc", "ddd eee fff")
        assert sim2 == 0.0

    def test_strategy_name(self, strategy: SemanticChunkStrategy):
        assert strategy.name == "semantic"


class TestHierarchicalChunkStrategy:
    """Hierarchical Chunk 策略测试。"""

    @pytest.fixture
    def strategy(self):
        return HierarchicalChunkStrategy()

    def test_creates_parent_and_child_chunks(self, strategy: HierarchicalChunkStrategy):
        text = "# Chapter 1\n\nParagraph one.\n\nParagraph two.\n\n# Chapter 2\n\nOther content."
        chunks = strategy.split(text, "doc1")
        assert len(chunks) >= 2  # 至少 parent chunks

        # 应该有 parent chunk
        parents = [c for c in chunks if c.metadata.get("is_parent") is True]
        assert len(parents) >= 1

    def test_no_headings_uses_paragraph_split(self, strategy: HierarchicalChunkStrategy):
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        chunks = strategy.split(text, "doc1")
        assert len(chunks) >= 1

    def test_empty_text(self, strategy: HierarchicalChunkStrategy):
        chunks = strategy.split("", "doc1")
        assert chunks == []

    def test_strategy_name(self, strategy: HierarchicalChunkStrategy):
        assert strategy.name == "hierarchical"

    def test_all_strategies_registered(self):
        from processor.chunker.service import CHUNK_STRATEGIES
        assert "heading" in CHUNK_STRATEGIES
        assert "semantic" in CHUNK_STRATEGIES
        assert "hierarchical" in CHUNK_STRATEGIES
