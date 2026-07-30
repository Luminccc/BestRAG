"""ParsedDocument 模型测试。"""

from document.model import ParsedDocument, TextBlock


class TestTextBlock:
    """TextBlock 模型测试。"""

    def test_default_values(self):
        block = TextBlock()
        assert block.type == "paragraph"
        assert block.level == 0
        assert block.content == ""

    def test_heading_block(self):
        block = TextBlock(type="heading", level=2, content="Introduction")
        assert block.type == "heading"
        assert block.level == 2
        assert block.content == "Introduction"

    def test_custom_metadata(self):
        block = TextBlock(type="paragraph", content="text", metadata={"page": 5})
        assert block.metadata["page"] == 5


class TestParsedDocument:
    """ParsedDocument 模型测试。"""

    def test_default_values(self):
        doc = ParsedDocument()
        assert doc.content == ""
        assert doc.metadata == {}
        assert doc.blocks == []

    def test_with_metadata_and_blocks(self):
        doc = ParsedDocument(
            content="Full text content",
            metadata={"source": "test.md", "author": "test"},
            blocks=[
                TextBlock(type="heading", level=1, content="Title"),
                TextBlock(type="paragraph", content="Content"),
            ],
        )
        assert doc.content == "Full text content"
        assert doc.metadata["source"] == "test.md"
        assert len(doc.blocks) == 2

    def test_blocks_content_matches(self):
        doc = ParsedDocument(
            content="# Title\n\nContent",
            blocks=[
                TextBlock(type="heading", level=1, content="Title"),
            ],
        )
        assert doc.blocks[0].content == "Title"
