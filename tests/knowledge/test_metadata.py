"""Metadata 模型和提取器测试。"""

from datetime import datetime

from document.model import ParsedDocument, TextBlock
from document.strategy import MetadataExtractor
from processor.chunker.model import ChunkMetadata


class TestChunkMetadata:
    """ChunkMetadata 模型测试。"""

    def test_default_values(self):
        meta = ChunkMetadata()
        assert meta.document_id == ""
        assert meta.chunk_index == 0
        assert meta.strategy == ""
        assert meta.page is None

    def test_with_values(self):
        meta = ChunkMetadata(
            document_id="doc1",
            chunk_index=3,
            strategy="recursive",
            page=5,
            heading="Introduction",
            heading_level=1,
            position=100,
            token_count=50,
        )
        assert meta.document_id == "doc1"
        assert meta.chunk_index == 3
        assert meta.strategy == "recursive"
        assert meta.page == 5

    def test_extra_fields(self):
        meta = ChunkMetadata(extra={"custom": "value"})
        assert meta.extra["custom"] == "value"


class TestMetadataExtractor:
    """MetadataExtractor 测试。"""

    def test_extract_document_metadata(self):
        parsed = ParsedDocument(
            content="Full content",
            metadata={"author": "test"},
            blocks=[
                TextBlock(type="heading", level=1, content="Title"),
                TextBlock(type="heading", level=2, content="Section"),
                TextBlock(type="paragraph", content="Some text."),
            ],
        )
        meta = MetadataExtractor.extract_document_metadata(
            parsed, source="test.md", parser_name="test_parser"
        )
        assert meta["source"] == "test.md"
        assert meta["parser"] == "test_parser"
        assert meta["author"] == "test"
        assert meta["heading_count"] == 2
        assert meta["max_heading_level"] == 2
        assert meta["block_count"] == 3

    def test_extract_empty_document(self):
        parsed = ParsedDocument()
        meta = MetadataExtractor.extract_document_metadata(parsed)
        assert meta["block_count"] == 0
        assert meta["char_count"] == 0

    def test_extract_block_structure(self):
        parsed = ParsedDocument(
            blocks=[
                TextBlock(type="heading", level=1, content="Title"),
                TextBlock(type="paragraph", content="Hello"),
            ],
        )
        blocks = MetadataExtractor.extract_block_structure(parsed)
        assert len(blocks) == 2
        assert blocks[0]["heading"] == "Title"
