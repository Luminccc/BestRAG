"""Document 验证检查 — 验证 DocumentService 产出结果。

检查项：
1. Document 对象是否成功生成
2. Document.id 是否存在
3. Document.content 是否非空
4. Document.metadata 是否包含 filename 和 file_type
"""

from time import time

from document.model import Document
from validation.model import ValidationReport


def check_document(
    doc: Document | None,
    parser_name: str | None = None,
) -> ValidationReport:
    """检查 Document 对象完整性。

    Args:
        doc:          DocumentService 返回的 Document（可能为 None）。
        parser_name:  实际使用的 Parser 名称，用于报告。

    Returns:
        包含各检查项结果的 ValidationReport。
    """
    start = time()
    module = "document"

    # 检查 1：Document 是否生成
    if doc is None:
        return ValidationReport.fail(
            module,
            message="Document 生成失败：返回值为 None",
        ).complete(start)

    # 检查 2：ID 是否存在
    if not doc.id:
        return ValidationReport.fail(
            module,
            message="Document.id 为空",
            parser=parser_name,
            document_id=doc.id,
        ).complete(start)

    # 检查 3：内容是否为空
    if not doc.content.strip():
        return ValidationReport.fail(
            module,
            message="Document content is empty",
            parser=parser_name,
            document_id=doc.id,
            content_length=0,
        ).complete(start)

    # 检查 4：Metadata 完整性
    meta = doc.metadata
    meta_errors: list[str] = []
    if not meta.filename:
        meta_errors.append("filename 为空")
    if not meta.file_type:
        meta_errors.append("file_type 为空")

    if meta_errors:
        return ValidationReport.fail(
            module,
            message="Metadata 不完整: " + "; ".join(meta_errors),
            parser=parser_name,
            document_id=doc.id,
            content_length=len(doc.content),
            metadata_errors=meta_errors,
        ).complete(start)

    # 全部通过
    return ValidationReport.ok(
        module,
        parser=parser_name or "unknown",
        document_id=doc.id,
        content_length=len(doc.content),
        file_type=meta.file_type.value if hasattr(meta.file_type, "value") else str(meta.file_type),
        filename=meta.filename,
    ).complete(start)
