"""Retrieval 模块测试文件。

用于验证整个检索流程是否正常工作。
"""

import asyncio
from retrieval.embedding.service import EmbeddingService
from retrieval.vectorstore.service import VectorStoreService
from retrieval.retriever.service import RetrievalService
from retrieval.reranker.service import RerankService
from retrieval.pipeline import RetrievalPipeline


def test_retrieval_pipeline():
    """测试检索流程。"""
    print("开始测试检索流程...")

    # 创建服务实例
    embedding_service = EmbeddingService()
    vector_store_service = VectorStoreService()
    retrieval_service = RetrievalService()
    rerank_service = RerankService()

    # 创建流程实例
    pipeline = RetrievalPipeline(
        embedding_service=embedding_service,
        vector_store_service=vector_store_service,
        retrieval_service=retrieval_service,
        rerank_service=rerank_service
    )

    # 准备测试数据
    test_texts = [
        "Python is a high-level programming language",
        "Machine learning is a subset of artificial intelligence",
        "Vector databases are used for similarity search",
        "Retrieval-Augmented Generation combines retrieval and generation",
        "BestRAG is a framework for building RAG applications"
    ]

    print("1. 测试 Embedding 功能...")
    embeddings = embedding_service.embed_documents(test_texts)
    print(f"   成功生成 {len(embeddings)} 个向量，维度: {embeddings[0].dimension}")

    print("2. 测试 VectorStore 功能...")
    text_vectors = [emb.vector for emb in embeddings]
    ids = vector_store_service.add_texts(test_texts, text_vectors)
    print(f"   成功添加 {len(ids)} 个向量到向量存储")

    print("3. 测试 Retrieval 功能...")
    query = "What is machine learning?"
    results = retrieval_service.retrieve(query, top_k=3)
    print(f"   检索到 {len(results)} 个结果")
    for i, result in enumerate(results):
        print(f"     结果 {i+1}: '{result.content[:50]}...' (分数: {result.score:.3f})")

    print("4. 测试 Rerank 功能...")
    reranked_results = rerank_service.rerank(query, results)
    print(f"   重排序后 {len(reranked_results)} 个结果")
    for i, result in enumerate(reranked_results):
        print(f"     结果 {i+1}: '{result.content[:50]}...' (分数: {result.score:.3f})")

    print("5. 测试完整 Pipeline...")
    pipeline_results = pipeline.retrieve(query, top_k=3, use_rerank=True)
    print(f"   Pipeline 返回 {len(pipeline_results)} 个结果")

    print("\n所有测试完成！")


if __name__ == "__main__":
    test_retrieval_pipeline()