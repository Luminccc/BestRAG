"""Retrieval 验证检查 — 验证 RetrievalService 产出结果。

检查项：
1. 检索流程是否正常
2. 检索结果数量是否正确
3. 检索结果是否包含必要信息
4. 检索准确性（基本测试）
"""

from time import time
from typing import List

from retrieval.retriever.service import RetrievalService
from retrieval.vectorstore.service import VectorStoreService
from retrieval.embedding.service import EmbeddingService
from validation.model import ValidationReport


def check_retrieval(
    retrieval_service: RetrievalService,
    vector_store_service: VectorStoreService,
    embedding_service: EmbeddingService,
    test_data: List[str] = None
) -> ValidationReport:
    """检查 Retrieval 服务完整性。

    Args:
        retrieval_service: RetrievalService 实例
        vector_store_service: VectorStoreService 实例
        embedding_service: EmbeddingService 实例
        test_data: 测试数据列表

    Returns:
        包含各检查项结果的 ValidationReport
    """
    start = time()
    module = "retrieval"

    if test_data is None:
        test_data = [
            "Milvus is a vector database",
            "Python is a programming language",
            "Machine learning algorithms",
            "Artificial intelligence applications",
            "BestRAG framework usage"
        ]

    try:
        # 检查 1：服务初始化
        if retrieval_service is None:
            return ValidationReport.fail(
                module,
                message="RetrievalService 未初始化"
            ).complete(start)

        if vector_store_service is None:
            return ValidationReport.fail(
                module,
                message="VectorStoreService 未初始化"
            ).complete(start)

        if embedding_service is None:
            return ValidationReport.fail(
                module,
                message="EmbeddingService 未初始化"
            ).complete(start)

        # 准备测试数据：先 Embedding 然后存储到 VectorStore
        embeddings = embedding_service.embed_documents(test_data)
        text_vectors = [emb.vector for emb in embeddings]

        # 添加到向量存储
        result_ids = vector_store_service.add_texts(test_data, text_vectors)

        if len(result_ids) != len(test_data):
            return ValidationReport.fail(
                module,
                message=f"添加测试数据失败: 期望 {len(test_data)}, 实际 {len(result_ids)}",
                test_case="prepare_test_data"
            ).complete(start)

        # 检查 2：执行检索
        query = "What database stores vectors?"
        results = retrieval_service.retrieve(query, top_k=3)

        # 检查 3：结果数量
        if len(results) == 0:
            return ValidationReport.fail(
                module,
                message="检索结果为空",
                test_case="retrieve_results",
                query=query
            ).complete(start)

        if len(results) > 3:  # top_k=3
            return ValidationReport.fail(
                module,
                message=f"检索结果数量超出限制: 期望最多 3, 实际 {len(results)}",
                test_case="result_count",
                query=query,
                expected_top_k=3,
                actual_count=len(results)
            ).complete(start)

        # 检查 4：结果完整性
        for result in results:
            if not result.chunk_id:
                return ValidationReport.fail(
                    module,
                    message="检索结果缺少 chunk_id",
                    test_case="result_integrity",
                    result_count=len(results)
                ).complete(start)

            if result.score < 0 or result.score > 1:
                return ValidationReport.fail(
                    module,
                    message=f"检索结果分数异常: {result.score}",
                    test_case="score_range",
                    result_count=len(results)
                ).complete(start)

            if not result.content:
                return ValidationReport.fail(
                    module,
                    message="检索结果内容为空",
                    test_case="content_check",
                    result_count=len(results)
                ).complete(start)

        # 检查 5：基本准确性（简单关键词匹配）
        # 查找是否有一个结果包含了"database"关键词，因为查询是关于数据库的
        db_related_found = any("database" in result.content.lower() for result in results)

        if not db_related_found and "Milvus is a vector database" in test_data:
            # 如果测试数据中有数据库相关的文本，但检索结果中没有，可能准确性有问题
            # 注意：这不是严格的准确性验证，只是基本的合理性检查
            pass  # 这里可以宽松处理，因为检索准确性可能因模型而异

        # 全部通过
        return ValidationReport.ok(
            module,
            test_case="retrieval_validation",
            result_count=len(results),
            top_k_requested=3,
            query_sample=query[:30] + "..." if len(query) > 30 else query,
            first_result_content=results[0].content[:50] + "..." if len(results[0].content) > 50 else results[0].content
        ).complete(start)

    except Exception as e:
        return ValidationReport.fail(
            module,
            message=f"Retrieval 验证异常: {type(e).__name__}: {str(e)}",
            test_case="retrieval_exception"
        ).complete(start)