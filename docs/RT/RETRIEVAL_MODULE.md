# BestRAG Retrieval 模块

基于 ADR-013 设计文档实现的 Retrieval 模块，为 BestRAG 提供检索增强生成（RAG）能力。

## 架构概览

```
用户 Query
    |
    v
Embedding
    |
    v
Vector Store (Milvus)
    |
    v
Retrieval
    |
    v
Rerank (可选)
    |
    v
Context
```

## 模块组成

### 1. Core 模块
- 配置管理
- 服务注册中心
- 日志记录
- 异常处理
- 工具函数

### 2. Embedding 模块
- 抽象接口：`BaseEmbedding`
- 模型：`EmbeddingResult`
- Provider：`BGEEmbedding` (V1)
- 服务：`EmbeddingService`

### 3. VectorStore 模块
- 抽象接口：`BaseVectorStore`
- 模型：`VectorStoreResult`, `SearchResult`
- Provider：`MilvusVectorStore` (V1)
- 服务：`VectorStoreService`

### 4. Retrieval 模块
- 模型：`RetrievalResult`, `RetrievalQuery`
- 服务：`RetrievalService`
- 流程编排：`RetrievalPipeline`

### 5. Rerank 模块
- 抽象接口：`BaseReranker`
- Provider：`BGEReranker` (V1)
- 服务：`RerankService`

## V1 版本功能

- [x] Document Chunk 向量化
- [x] Query 向量化
- [x] 向量保存
- [x] 相似度搜索
- [x] Query 检索
- [x] Top-K 返回
- [x] 基础二次排序接口

## 验证功能

- [x] Embedding 验证
- [x] VectorStore 验证
- [x] Retrieval 验证
- [x] Rerank 验证

## 使用示例

```python
from retrieval.pipeline import RetrievalPipeline

# 创建检索流程
pipeline = RetrievalPipeline()

# 执行检索
results = pipeline.retrieve(
    query="什么是机器学习？",
    top_k=5,
    use_rerank=True  # 启用重排序
)

# 输出结果
for result in results:
    print(f"分数: {result.score}, 内容: {result.content}")
```

## API 接口

### 验证 API

- `POST /validation/retrieval/embedding` - Embedding 验证
- `POST /validation/retrieval/vectorstore` - VectorStore 验证
- `POST /validation/retrieval/search` - Retrieval 验证
- `POST /validation/retrieval/rerank` - Rerank 验证
- `POST /validation/retrieval/all` - 完整回归测试

## 依赖

- sentence-transformers
- pymilvus
- FlagEmbedding
- numpy

## 未来扩展

- Cache
- Hybrid Search
- Multi Vector Retrieval
- Metadata Filtering Engine
- Knowledge Graph Retrieval
- Agent Retrieval
```