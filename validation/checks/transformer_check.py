"""Transformer 验证检查 — 验证 SchemaTransformer 产出结果。

检查项：
1. Document 对象是否存在
2. metadata.extra 包含 source_file
3. metadata.extra 包含 document_id（与 Document.id 一致）
4. metadata.created_time 不为空
"""

from time import time

from document.model import Document
from validation.model import ValidationReport


def check_transformer(doc: Document | None) -> ValidationReport:
    """检查 SchemaTransformer 处理后的 Document 标准化完整性。

    Args:
        doc: TransformerService.transform() 返回的 Document。

    Returns:
        包含溯源信息和字段状态的 ValidationReport。
    """
    start = time()
    module = "processor/transformer"

    if doc is None:
        return ValidationReport.fail(
            module,
            message="Transformer 输出为 None",
        ).complete(start)

    extra = doc.metadata.extra

    # 检查 source_file
    source_file = extra.get("source_file")
    if not source_file:
        return ValidationReport.fail(
            module,
            message="metadata.extra.source_file 缺失或为空",
            document_id=doc.id,
        ).complete(start)

    # 检查 document_id
    extra_doc_id = extra.get("document_id")
    if not extra_doc_id:
        return ValidationReport.fail(
            module,
            message="metadata.extra.document_id 缺失或为空",
            document_id=doc.id,
        ).complete(start)

    # 检查 document_id 一致性
    if extra_doc_id != doc.id:
        return ValidationReport.fail(
            module,
            message=f"metadata.extra.document_id ({extra_doc_id}) "
                    f"与 Document.id ({doc.id}) 不一致",
            document_id=doc.id,
        ).complete(start)

    # 检查 created_time
    if doc.metadata.created_time is None:
        return ValidationReport.fail(
            module,
            message="metadata.created_time 为空",
            document_id=doc.id,
        ).complete(start)

    return ValidationReport.ok(
        module,
        document_id=doc.id,
        source_file=source_file,
        filename=doc.metadata.filename,
        file_type=doc.metadata.file_type.value if hasattr(doc.metadata.file_type, "value") else str(doc.metadata.file_type),
        created_time=str(doc.metadata.created_time),
    ).complete(start)
