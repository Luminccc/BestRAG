"""Pipeline 验证检查 — 验证 ProcessorService 管线产出。

检查项：
1. ProcessedDocument 对象是否存在
2. Document 是否存在
3. Chunk 列表非空
4. Chunk.document_id == Document.id
5. Transformer 溯源信息存在
"""

from time import time

from processor.model import ProcessedDocument
from validation.model import ValidationReport


def check_pipeline(
    result: ProcessedDocument | None,
    strategy: str | None = None,
) -> ValidationReport:
    """检查 Pipeline 处理结果的完整性。

    Args:
        result: ProcessorService.process() 返回的 ProcessedDocument。
        strategy: 使用的 Chunk 策略名。

    Returns:
        包含管线各阶段状态的 ValidationReport。
    """
    start = time()
    module = "processor/pipeline"

    # 检查 1：ProcessedDocument 非空
    if result is None:
        return ValidationReport.fail(
            module,
            message="Pipeline 输出为 None",
        ).complete(start)

    doc = result.document
    chunks = result.chunks

    # 检查 2：Document 存在
    if doc is None:
        return ValidationReport.fail(
            module,
            message="ProcessedDocument.document 为 None",
        ).complete(start)

    if not doc.content.strip():
        return ValidationReport.fail(
            module,
            message="文档内容为空（可能 Cleaner 异常或原始内容为空）",
        ).complete(start)

    # 检查 3：Chunk 列表非空
    if not chunks:
        return ValidationReport.fail(
            module,
            message="Chunk 列表为空（可能 Chunker 异常）",
            document_id=doc.id,
        ).complete(start)

    # 检查 4：Chunk 关联一致性
    for ch in chunks:
        if ch.document_id != doc.id:
            return ValidationReport.fail(
                module,
                message=f"Chunk [{ch.index}] document_id ({ch.document_id}) "
                        f"与 Document.id ({doc.id}) 不匹配",
                document_id=doc.id,
                chunk_index=ch.index,
            ).complete(start)

    # 检查 5：Transformer 溯源信息
    extra = doc.metadata.extra
    if not extra.get("source_file"):
        return ValidationReport.fail(
            module,
            message="Transformer 溯源信息缺失：source_file 为空",
            document_id=doc.id,
        ).complete(start)
    if not extra.get("document_id"):
        return ValidationReport.fail(
            module,
            message="Transformer 溯源信息缺失：document_id 为空",
            document_id=doc.id,
        ).complete(start)

    # 统计
    chunk_lengths = [len(c.content) for c in chunks]

    return ValidationReport.ok(
        module,
        strategy=strategy or "recursive",
        document_id=doc.id,
        filename=doc.metadata.filename,
        chunk_count=len(chunks),
        avg_chunk_length=round(sum(chunk_lengths) / len(chunks), 1) if chunk_lengths else 0,
        cleaner_applied=extra.get("cleaned", False),
        transformer_applied=bool(extra.get("source_file")),
    ).complete(start)
