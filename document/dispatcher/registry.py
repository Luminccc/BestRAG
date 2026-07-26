"""Parser Registry — 文件扩展名到 Provider 类的静态映射。

集中注册所有 Provider，新增格式时只需在此添加一条映射。
禁止 Provider 模块反向修改此 Registry，避免循环依赖。
"""

from document.parser import MarkItDownProvider, OpenDataLoaderProvider

# 扩展名 → Provider 类（扩展名不含前导点号，全小写）
PARSER_REGISTRY: dict[str, type] = {
    # OpenDataLoader（PDF 专用）
    "pdf": OpenDataLoaderProvider,
    # MarkItDown（Office + 纯文本）
    "docx": MarkItDownProvider,
    "pptx": MarkItDownProvider,
    "xlsx": MarkItDownProvider,
    "html": MarkItDownProvider,
    "md":   MarkItDownProvider,
    "txt":  MarkItDownProvider,
}
