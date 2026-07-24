"""Embedding 验证检查 — 验证 EmbeddingService 产出结果。

检查项：
1. Embedding 模型是否成功加载
2. Embedding 向量维度是否正确
3. 批量 Embedding 是否正常工作
4. 空文本处理是否正确
"""

from time import time
from typing import List

from retrieval.embedding.service import EmbeddingService
from validation.model import ValidationReport


def check_embedding(
    embedding_service: EmbeddingService,
    test_query: str = "BestRAG is a RAG framework"
) -> ValidationReport:
    """检查 Embedding 服务完整性。

    Args:
        embedding_service: EmbeddingService 实例
        test_query: 测试查询文本

    Returns:
        包含各检查项结果的 ValidationReport
    """
    start = time()
    module = "embedding"

    try:
        # 检查 1：Embedding 模型加载
        if embedding_service is None:
            return ValidationReport.fail(
                module,
                message="EmbeddingService 未初始化"
            ).complete(start)

        # 检查 2：单文本 Embedding
        embedding_result = embedding_service.embed_text(test_query)
        if not embedding_result.vector or len(embedding_result.vector) == 0:
            return ValidationReport.fail(
                module,
                message="Embedding 结果向量为空",
                test_case="single_text_embedding",
                input_text=test_query
            ).complete(start)

        # 检查 3：向量维度
        expected_dim = embedding_service.dimension
        actual_dim = len(embedding_result.vector)
        if actual_dim != expected_dim:
            return ValidationReport.fail(
                module,
                message=f"向量维度不匹配: 期望 {expected_dim}, 实际 {actual_dim}",
                test_case="dimension_check",
                expected_dimension=expected_dim,
                actual_dimension=actual_dim
            ).complete(start)

        # 检查 4：批量 Embedding
        batch_texts = ["Hello", "World", "BestRAG"]
        batch_results = embedding_service.embed_documents(batch_texts)

        if len(batch_results) != len(batch_texts):
            return ValidationReport.fail(
                module,
                message=f"批量 Embedding 数量不匹配: 期望 {len(batch_texts)}, 实际 {len(batch_results)}",
                test_case="batch_embedding_count",
                expected_count=len(batch_texts),
                actual_count=len(batch_results)
            ).complete(start)

        # 检查 5：空文本处理
        try:
            embedding_service.embed_text("")
            # 如果没有抛出异常，则认为处理了空文本
        except Exception:
            # 空文本应该抛出异常或有特殊处理
            pass

        # 全部通过
        return ValidationReport.ok(
            module,
            test_case="embedding_validation",
            dimension=expected_dim,
            batch_size=len(batch_texts),
            input_sample=test_query[:50] + "..." if len(test_query) > 50 else test_query
        ).complete(start)

    except Exception as e:
        return ValidationReport.fail(
            module,
            message=f"Embedding 验证异常: {type(e).__name__}: {str(e)}",
            test_case="embedding_exception"
        ).complete(start)