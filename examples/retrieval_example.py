"""
BestRAG Retrieval 模块使用示例

展示如何使用新实现的检索模块
"""

from retrieval.embedding.service import EmbeddingService
from retrieval.vectorstore.service import VectorStoreService
from retrieval.retriever.service import RetrievalService
from retrieval.reranker.service import RerankService
from retrieval.pipeline import RetrievalPipeline


def example_basic_usage():
    """基本使用示例"""
    print("=== Basic Usage Example ===")

    # 1. 创建服务实例
    embedding_service = EmbeddingService()
    vector_store_service = VectorStoreService()
    retrieval_service = RetrievalService(
        embedding_service=embedding_service,
        vector_store_service=vector_store_service
    )
    rerank_service = RerankService()

    # 2. 准备测试数据
    documents = [
        "Python是一种高级编程语言，广泛用于数据科学和机器学习。",
        "机器学习是人工智能的一个分支，专注于算法和统计模型。",
        "向量数据库专门用于存储和检索高维向量，常用于相似性搜索。",
        "检索增强生成（RAG）结合了信息检索和文本生成技术。",
        "BestRAG是一个企业级知识库RAG框架。"
    ]

    # 3. 对文档进行向量化并存储
    embeddings = embedding_service.embed_documents(documents)
    vectors = [emb.vector for emb in embeddings]
    ids = vector_store_service.add_texts(documents, vectors)

    print(f"成功添加 {len(ids)} 个文档到向量存储")

    # 4. 执行检索
    query = "机器学习是什么？"
    results = retrieval_service.retrieve(query, top_k=3)

    print(f"\n检索到 {len(results)} 个结果:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. 分数: {result.score:.3f}, 内容: {result.content[:50]}...")

    # 5. 执行重排序（可选）
    reranked_results = rerank_service.rerank(query, results)

    print(f"\n重排序后 {len(reranked_results)} 个结果:")
    for i, result in enumerate(reranked_results, 1):
        print(f"  {i}. 分数: {result.score:.3f}, 内容: {result.content[:50]}...")


def example_pipeline_usage():
    """使用完整流水线的示例"""
    print("\n=== Pipeline Usage Example ===")

    # 使用预配置的流水线
    pipeline = RetrievalPipeline()

    # 准备一些文档用于演示
    demo_docs = [
        "自然语言处理是计算机科学和人工智能的分支。",
        "深度学习使用多层神经网络进行特征学习。",
        "向量嵌入将文本转换为数值向量表示。",
        "语义搜索基于意义而非关键词匹配文档。"
    ]

    # 将演示文档添加到向量存储
    embedding_service = pipeline._embedding_service
    vector_store_service = pipeline._vector_store_service

    embeddings = embedding_service.embed_documents(demo_docs)
    vectors = [emb.vector for emb in embeddings]
    vector_store_service.add_texts(demo_docs, vectors)

    # 执行检索
    query = "什么是深度学习？"
    results = pipeline.retrieve(query, top_k=2, use_rerank=True)

    print(f"针对查询 '{query}' 检索到 {len(results)} 个结果:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. 分数: {result.score:.3f}")
        print(f"     内容: {result.content}")


def example_advanced_configuration():
    """高级配置示例"""
    print("\n=== Advanced Configuration Example ===")

    # 自定义Embedding模型
    embedding_service = EmbeddingService()

    # 自定义向量存储
    vector_store_service = VectorStoreService()

    # 自定义检索服务
    retrieval_service = RetrievalService(
        embedding_service=embedding_service,
        vector_store_service=vector_store_service
    )

    # 自定义重排序服务
    rerank_service = RerankService()

    # 自定义流水线
    pipeline = RetrievalPipeline(
        embedding_service=embedding_service,
        vector_store_service=vector_store_service,
        retrieval_service=retrieval_service,
        rerank_service=rerank_service
    )

    print("自定义配置的流水线创建成功!")
    print(f"Embedding 维度: {embedding_service.dimension}")
    print(f"VectorStore 维度: {vector_store_service.get_dimension()}")


if __name__ == "__main__":
    print("BestRAG Retrieval 模块使用示例")
    print("=" * 50)

    example_basic_usage()
    example_pipeline_usage()
    example_advanced_configuration()

    print("\n" + "=" * 50)
    print("示例执行完成!")