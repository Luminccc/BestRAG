"""Rerank 验证检查 — 验证 RerankService 产出结果。

检查项：
1. 重排序功能是否正常
2. 排序顺序是否发生变化（验证重排序效果）
3. 分数是否合理
4. 重排序后结果完整性
"""

from time import time
from typing import List

from retrieval.reranker.service import RerankService
from retrieval.retriever.model import RetrievalResult
from validation.model import ValidationReport


def check_rerank(
    rerank_service: RerankService,
    test_query: str = "vector database technology",
    test_documents: List[RetrievalResult] = None
) -> ValidationReport:
    """检查 Rerank 服务完整性。

    Args:
        rerank_service: RerankService 实例
        test_query: 测试查询文本
        test_documents: 测试文档列表

    Returns:
        包含各检查项结果的 ValidationReport
    """
    start = time()
    module = "rerank"

    if test_documents is None:
        # 创建测试文档，模拟检索结果
        test_documents = [
            RetrievalResult(
                chunk_id="doc1",
                score=0.7,
                content="Python programming language and development",
                metadata={"source": "test", "type": "programming"}
            ),
            RetrievalResult(
                chunk_id="doc2",
                score=0.8,
                content="Vector databases like Milvus and their applications",
                metadata={"source": "test", "type": "database"}
            ),
            RetrievalResult(
                chunk_id="doc3",
                score=0.5,
                content="Machine learning and artificial intelligence concepts",
                metadata={"source": "test", "type": "ml_ai"}
            ),
            RetrievalResult(
                chunk_id="doc4",
                score=0.6,
                content="BestRAG framework for retrieval augmented generation",
                metadata={"source": "test", "type": "framework"}
            )
        ]

    try:
        # 检查 1：服务初始化
        if rerank_service is None:
            return ValidationReport.fail(
                module,
                message="RerankService 未初始化"
            ).complete(start)

        # 检查 2：原始文档列表
        if not test_documents:
            return ValidationReport.fail(
                module,
                message="测试文档列表为空",
                test_case="input_check"
            ).complete(start)

        # 记录原始排序和分数
        original_scores = [doc.score for doc in test_documents]
        original_ids = [doc.chunk_id for doc in test_documents]

        # 检查 3：执行重排序
        reranked_results = rerank_service.rerank(test_query, test_documents)

        # 检查 4：重排序结果数量
        if len(reranked_results) != len(test_documents):
            return ValidationReport.fail(
                module,
                message=f"重排序结果数量不匹配: 期望 {len(test_documents)}, 实际 {len(reranked_results)}",
                test_case="result_count",
                original_count=len(test_documents),
                reranked_count=len(reranked_results)
            ).complete(start)

        # 检查 5：重排序后分数合理性
        for result in reranked_results:
            if result.score < 0:
                return ValidationReport.fail(
                    module,
                    message=f"重排序结果分数小于0: {result.score}",
                    test_case="score_range",
                    chunk_id=result.chunk_id
                ).complete(start)

        # 检查 6：ID 是否一致（应该保持相同文档，但顺序可能变化）
        reranked_ids = [result.chunk_id for result in reranked_results]
        if set(original_ids) != set(reranked_ids):
            return ValidationReport.fail(
                module,
                message="重排序后文档 ID 发生变化",
                test_case="id_integrity",
                original_ids=original_ids,
                reranked_ids=reranked_ids
            ).complete(start)

        # 检查 7：排序是否发生变化（验证重排序确实发生了）
        original_first_id = original_ids[0] if original_ids else None
        reranked_first_id = reranked_ids[0] if reranked_ids else None

        sort_changed = original_first_id != reranked_first_id

        # 检查 8：内容完整性
        for i, result in enumerate(reranked_results):
            original_doc = next((doc for doc in test_documents if doc.chunk_id == result.chunk_id), None)
            if original_doc is None:
                return ValidationReport.fail(
                    module,
                    message=f"重排序结果中找不到原始文档: {result.chunk_id}",
                    test_case="document_integrity",
                    position=i
                ).complete(start)

            # 检查内容是否保持不变
            if original_doc.content != result.content:
                return ValidationReport.fail(
                    module,
                    message=f"文档内容在重排序过程中发生改变: {result.chunk_id}",
                    test_case="content_integrity",
                    chunk_id=result.chunk_id
                ).complete(start)

        # 全部通过
        return ValidationReport.ok(
            module,
            test_case="rerank_validation",
            original_count=len(test_documents),
            reranked_count=len(reranked_results),
            sort_changed=sort_changed,
            query_sample=test_query[:30] + "..." if len(test_query) > 30 else test_query,
            original_first_id=original_first_id,
            reranked_first_id=reranked_first_id
        ).complete(start)

    except Exception as e:
        return ValidationReport.fail(
            module,
            message=f"Rerank 验证异常: {type(e).__name__}: {str(e)}",
            test_case="rerank_exception"
        ).complete(start)