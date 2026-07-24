# BestRAG 运行指南

## 前置服务（需先启动）

所有模型通过 FastAPI 接口接入，启动 BestRAG 前确保以下服务已运行：

| 服务 | 端口 | 说明 |
|------|------|------|
| Attu (Milvus GUI) | 8000 | 可选，可视化工具 |
| BGE-M3 Embedding | 8001 | 文本向量化 API |
| BGE-Rerank | 8002 | 重排序 API |
| Milvus | 19530 | 向量数据库 |

## 依赖安装

```bash
uv sync
```

## 配置

项目根目录 `config.yaml` 为配置入口，所有模型走 API：

```yaml
retrieval:
  embedding_api_url: "http://localhost:8001/embed"
  embedding_dim: 1024
  vectorstore_type: "milvus"
  milvus_host: "localhost"
  milvus_port: 19530
  milvus_collection_prefix: "bestrag"
  rerank_api_url: "http://localhost:8002/rerank"
  top_k: 10
```

也支持环境变量覆盖：

```bash
export BESTRAG_EMBEDDING_API_URL="http://localhost:8001/embed"
export BESTRAG_RERANK_API_URL="http://localhost:8002/rerank"
export BESTRAG_MILVUS_HOST="localhost"
export BESTRAG_MILVUS_PORT=19530
export BESTRAG_TOP_K=10
```

## 启动应用

```bash
uv run uvicorn main:app --reload --port 8000
```

## 验证各模块

```bash
# Embedding 验证
curl -X POST "http://localhost:8000/validation/retrieval/embedding"

# VectorStore 验证
curl -X POST "http://localhost:8000/validation/retrieval/vectorstore"

# Rerank 验证
curl -X POST "http://localhost:8000/validation/retrieval/rerank"

# 全链路检索验证
curl -X POST "http://localhost:8000/validation/retrieval/search"
```
