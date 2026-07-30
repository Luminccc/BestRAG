"""MetadataExtractor — 从 ParsedDocument 中提取结构化元数据。

职责：
- 从 ParsedDocument 的 blocks 和 content 中提取文档元数据
- 为 Chunk 策略提供文档结构信息（标题层级、段落分布等）
"""

from typing import Any, Dict

from document.model import ParsedDocument


class MetadataExtractor:
    """元数据提取器。

    从标准化 ParsedDocument 中提取文档级元数据和结构信息。
    """

    @staticmethod
    def extract_document_metadata(
        parsed: ParsedDocument,
        source: str = "",
        parser_name: str = "",
    ) -> Dict[str, Any]:
        """提取文档级元数据。

        Args:
            parsed:     标准化解析文档。
            source:     来源标识（如文件路径或 URL）。
            parser_name: 使用的解析器名称。

        Returns:
            文档级元数据字典。
        """
        metadata = {
            **parsed.metadata,
            "source": source,
            "parser": parser_name,
        }

        # 从 blocks 中统计结构信息
        headings = [b for b in parsed.blocks if b.type == "heading"]
        if headings:
            metadata["heading_count"] = len(headings)
            metadata["max_heading_level"] = max(b.level for b in headings)

        metadata["block_count"] = len(parsed.blocks)
        metadata["char_count"] = len(parsed.content)

        return metadata

    @staticmethod
    def extract_block_structure(parsed: ParsedDocument) -> list[Dict[str, Any]]:
        """提取块级结构信息，供 Chunk 策略参考。

        Returns:
            每个 block 的结构摘要列表。
        """
        return [
            {
                "type": b.type,
                "level": b.level,
                "length": len(b.content),
                "heading": b.content if b.type == "heading" else "",
            }
            for b in parsed.blocks
        ]
