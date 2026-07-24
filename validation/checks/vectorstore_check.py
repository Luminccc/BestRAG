"""VectorStore 验证检查 — 验证 VectorStoreService 产出结果。

检查项：
1. VectorStore 连接是否正常
2. 添加向量是否成功
3. 搜索功能是否正常
4. 检索结果是否包含必要的信息
"""

from time import time
from typing import List

from retrieval.vectorstore.service import VectorStoreService
from retrieval.embedding.service import EmbeddingService
from validation.model import ValidationReport


def check_vectorstore(
    vector_store_service: VectorStoreService,
    embedding_service: EmbeddingService,
    test_texts: List[str] = None
) -> ValidationReport:
    """检查 VectorStore 服务完整性。

    Args:
        vector_store_service: VectorStoreService 实例
        embedding_service: EmbeddingService 实例
        test_texts: 测试文本列表

    Returns:
        包含各检查项结果的 ValidationReport
    """
    start = time()
    module = "vectorstore"

    if test_texts is None:
        test_texts = [
            "Python programming language",
            "Machine learning model",
            "Artificial intelligence",
            "BestRAG is a RAG framework"
        ]

    try:
        # 检查 1：VectorStore 连接和初始化
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

        # 检查 2：Embedding 测试文本
        embeddings = embedding_service.embed_documents(test_texts)
        if len(embeddings) != len(test_texts):
            return ValidationReport.fail(
                module,
                message=f"Embedding 数量不匹配: 期望 {len(test_texts)}, 实际 {len(embeddings)}",
                test_case="embedding_count"
            ).complete(start)

        # 检查 3：添加向量到 VectorStore
        text_vectors = [emb.vector for emb in embeddings]
        result_ids = vector_store_service.add_texts(test_texts, text_vectors)

        if len(result_ids) != len(test_texts):
            return ValidationReport.fail(
                module,
                message=f"添加向量数量不匹配: 期望 {len(test_texts)}, 实际 {len(result_ids)}",
                test_case="add_vectors"
            ).complete(start)

        # 检查 4：搜索功能
        query_text = "programming"
        query_embedding = embedding_service.embed_text(query_text)

        search_result = vector_store_service.similarity_search(
            query=query_text,
            query_embedding=query_embedding.vector,
            top_k=2
        )

        # 检查 5：搜索结果完整性
        if len(search_result.results) == 0:
            return ValidationReport.fail(
                module,
                message="搜索结果为空",
                test_case="search_result",
                query=query_text
            ).complete(start)

        # 检查结果是否包含必要的信息
        for result in search_result.results:
            if not result.id:
                return ValidationReport.fail(
                    module,
                    message="搜索结果缺少 chunk_id",
                    test_case="result_integrity",
                    result_count=len(search_result.results)
                ).complete(start)

            if result.score < 0 or result.score > 1:
                return ValidationReport.fail(
                    module,
                    message=f"搜索结果分数异常: {result.score}",
                    test_case="score_range",
                    result_count=len(search_result.results)
                ).complete(start)

            if not result.content:
                return ValidationReport.fail(
                    module,
                    message="搜索结果内容为空",
                    test_case="content_check",
                    result_count=len(search_result.results)
                ).complete(start)

        # 检查 6：向量维度一致性
        vector_dim = vector_store_service.get_dimension()
        embedding_dim = embedding_service.dimension
        if vector_dim != embedding_dim:
            return ValidationReport.fail(
                module,
                message=f"向量维度不一致: VectorStore {vector_dim}, Embedding {embedding_dim}",
                test_case="dimension_consistency"
            ).complete(start)

        # 全部通过
        return ValidationReport.ok(
            module,
            test_case="vectorstore_validation",
            dimension=vector_dim,
            inserted_count=len(result_ids),
            search_results=len(search_result.results),
            top_k=search_result.top_k,
            query=search_result.query
        ).complete(start)

    except Exception as e:
        return ValidationReport.fail(
            module,
            message=f"VectorStore 验证异常: {type(e).__name__}: {str(e)}",
            test_case="vectorstore_exception"
        ).complete(start)