"""Processor 验证检查 — 验证 Cleaner 产出结果。

检查项：
1. Document 对象是否存在
2. Document.content 是否非空
3. metadata.extra 是否标记 cleaned=True
4. 记录 original_length 和 cleaned_length
"""

from time import time

from document.model import Document
from validation.model import ValidationReport


def check_cleaner(doc: Document | None) -> ValidationReport:
    """检查 Cleaner 处理后的 Document 完整性。

    Args:
        doc: ProcessorService.process() 返回的 Document（可能为 None）。

    Returns:
        包含清洗前后对比的 ValidationReport。
    """
    start = time()
    module = "processor/cleaner"

    # 检查 1: Document 是否存在
    if doc is None:
        return ValidationReport.fail(
            module,
            message="Cleaner 输出为 None",
        ).complete(start)

    # 检查 2: 内容非空
    if not doc.content.strip():
        return ValidationReport.fail(
            module,
            message="Cleaner 输出内容为空",
            document_id=doc.id,
        ).complete(start)

    # 检查 3: 清洗标记
    extra = doc.metadata.extra
    cleaned = extra.get("cleaned", False)
    if not cleaned:
        return ValidationReport.fail(
            module,
            message="metadata.extra.cleaned 未标记为 True",
            document_id=doc.id,
        ).complete(start)

    # 全部通过
    original_len = extra.get("original_length", 0)
    cleaned_len = extra.get("cleaned_length", 0)

    return ValidationReport.ok(
        module,
        document_id=doc.id,
        original_length=original_len,
        cleaned_length=cleaned_len,
        reduction=original_len - cleaned_len,
    ).complete(start)
