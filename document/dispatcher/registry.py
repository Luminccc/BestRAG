"""Parser Registry — 文件扩展名到 Parser 类的静态映射。

集中注册所有 Parser，新增格式时只需在此添加一条映射。
禁止 Parser 模块反向修改此 Registry，避免循环依赖。
"""

from document.parser import DocxParser, MarkdownParser, PDFParser, TxtParser

# 扩展名 → Parser 类（扩展名不含前导点号，全小写）
PARSER_REGISTRY: dict[str, type] = {
    "pdf": PDFParser,
    "docx": DocxParser,
    "md": MarkdownParser,
    "txt": TxtParser,
}
