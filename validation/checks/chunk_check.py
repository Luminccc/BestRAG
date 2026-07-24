"""Chunk 验证检查 — 验证 ChunkService 产出结果。

检查项：
1. Chunk 列表非空
2. 每个 Chunk 的 content 非空
3. 每个 Chunk 的 document_id 与来源一致
4. 记录 chunk_count、avg_length、max_length
"""

from time import time

from processor.chunker.model import Chunk
from validation.model import ValidationReport


def check_chunk(
    chunks: list[Chunk] | None,
    document_id: str | None = None,
    strategy: str | None = None,
) -> ValidationReport:
    """检查 Chunk 列表完整性。

    Args:
        chunks:       ChunkService.chunk() 返回的列表（可能为 None）。
        document_id:  来源 Document 的 id，用于验证关联。
        strategy:     使用的策略名。

    Returns:
        包含 chunk 统计信息的 ValidationReport。
    """
    start = time()
    module = "processor/chunker"

    # 检查 1：列表非空
    if chunks is None:
        return ValidationReport.fail(
            module,
            message="Chunk 列表为 None",
            strategy=strategy,
        ).complete(start)

    if len(chunks) == 0:
        return ValidationReport.fail(
            module,
            message="Chunk 列表为空",
            strategy=strategy,
        ).complete(start)

    # 检查 2 + 3：每个 Chunk 的内容和 document_id
    for ch in chunks:
        if not ch.content.strip():
            return ValidationReport.fail(
                module,
                message=f"Chunk [{ch.index}] 内容为空",
                strategy=strategy,
                chunk_index=ch.index,
                chunk_id=ch.id,
            ).complete(start)

        if document_id and ch.document_id != document_id:
            return ValidationReport.fail(
                module,
                message=f"Chunk [{ch.index}] document_id 不匹配: "
                        f"{ch.document_id} != {document_id}",
                strategy=strategy,
            ).complete(start)

    # 统计
    lengths = [len(c.content) for c in chunks]
    total = len(chunks)
    avg = round(sum(lengths) / total, 1)
    max_len = max(lengths)
    min_len = min(lengths)

    return ValidationReport.ok(
        module,
        strategy=strategy or "unknown",
        chunk_count=total,
        avg_length=avg,
        max_length=max_len,
        min_length=min_len,
        document_id=document_id,
    ).complete(start)
