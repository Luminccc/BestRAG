<p align="center">
  <img src="static/console/img/logo.svg" alt="BestRAG Logo" width="180" />
</p>

<h1 align="center">BestRAG</h1>

<p align="center">
  企业级知识库 RAG 框架 —— 从文档到答案，一套完善的预设即可。
  <br/>
  <strong>Python 3.12+ · FastAPI · Milvus · BGE · OpenAI 兼容</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12%20|%203.13-blue" />
  <img src="https://img.shields.io/badge/version-0.1.0--alpha-orange" />
  <img src="https://img.shields.io/badge/license-MIT-green" />
</p>

---

## 概述

BestRAG 是一个面向企业场景的 **检索增强生成（RAG）框架**，提供从文档接入、解析、清洗、切分、向量化到检索和生成的完整链路。

项目设计遵循**分层架构**和**依赖倒置**原则，核心模块均通过 Provider 接口解耦，便于替换底层实现（如向量数据库、Embedding 模型、LLM 等）。

当前版本（v0.1.0-alpha）已覆盖 RAG 核心链路，并提供 Web 管理控制台和全面的验证中心，适合中小规模知识库快速搭建。

## 架构

```
                    ┌───────────────────────────────────┐
                    │        Feature Layer (API)         │
                    │  Knowledge Ingest · QA · Validation│
                    └──────────┬────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
   ┌────────────┐    ┌────────────────┐    ┌──────────────┐
   │  Document  │    │   Retrieval    │    │  Generation  │
   │ Processing │    │    Pipeline    │    │   Pipeline   │
   │            │    │                │    │              │
   │ · Ingress  │    │ · Embedding    │    │ · Context    │
   │ · Parser   │    │ · VectorStore  │    │ · Prompt     │
   │ · Cleaner  │    │ · BM25/Hybrid  │    │ · LLM        │
   │ · Chunker  │    │ · Reranker     │    │              │
   │ · Index    │    │ · Cache        │    │              │
   └────────────┘    └────────────────┘    └──────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
           ┌──────────────┐    ┌──────────────────┐
           │   Milvus     │    │  OpenAI 兼容 LLM  │
           │ 向量数据库    │    │  (DeepSeek/OpenAI) │
           └──────────────┘    └──────────────────┘
```

### 核心模块

| 模块 | 职责 | 关键接口 |
|------|------|---------|
| **ingress** | 统一文件入口（上传 / 本地 / 目录） | `IngressService` |
| **document** | 文档解析调度（markitdown / opendataloader） | `DocumentDispatcher` |
| **processor** | 文本清洗 + 切分 + 结构转换 | `TextCleaner`, `BaseChunkStrategy` |
| **indexing** | Chunk → Embedding → 写入向量库 | `IndexPipeline` |
| **retrieval** | 向量 / BM25 / Hybrid 检索 + 重排序 + 缓存 | `RetrievalPipelineV2` |
| **generation** | 上下文组装 → Prompt 构建 → LLM 生成 | `GenerationPipeline` |
| **validation** | 逐模块验证 + 场景验证 + 端到端检查 | `ValidationService` |

### 设计要点

- **Provider 生命周期** —— Embedding、VectorStore、Reranker 等重量级资源通过 `BaseProvider` 接口统一管理（`initialize` → `close`），由 `ResourceManager` 全局调度
- **插件式解析器** —— `DocumentDispatcher` 根据文件扩展名自动路由到对应 Parser，新增格式只需注册新 Parser
- **可替换的检索策略** —— 通过 `retrieval.strategy` 配置切换 `vector` / `bm25` / `hybrid`，无需改动代码
- **两级缓存** —— RetrievalCache（查询结果）+ EmbeddingCache（向量），支持 Redis 和内存后端，`index_version` 变更自动失效
- **验证中心** —— 每个模块都有独立验证检查，支持单模块调试和全链路回归，适合 CI 集成
- **统一配置** —— YAML 文件 + 环境变量覆盖，所有配置通过 `get_config()` 访问，禁止模块自行读取

## 快速开始

### 前置依赖

以下服务需提前启动：

| 服务 | 端口 | 用途 | 启动方式 |
|------|------|------|---------|
| Milvus | 19530 | 向量数据库 | `docker compose up milvus` |
| BGE-M3 Embedding API | 8001 | 文本向量化 | Docker / 独立服务 |
| BGE-Rerank API | 8002 | 检索结果重排序 | Docker / 独立服务 |

### 安装

```bash
# 克隆仓库
git clone https://github.com/your-org/bestrag.git
cd bestrag

# 安装依赖（使用 uv，推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 配置

```bash
# 复制配置模板
cp config.yaml config.local.yaml
# 编辑 config.local.yaml 中的服务地址

# 或用环境变量覆盖
export BESTRAG_EMBEDDING_API_URL="http://localhost:8001/embed"
export BESTRAG_RERANK_API_URL="http://localhost:8002/rerank"
export BESTRAG_MILVUS_HOST="localhost"
export BESTRAG_MILVUS_PORT=19530
export BESTRAG_LLM_API_KEY="sk-xxxx"
export BESTRAG_LLM_BASE_URL="https://api.deepseek.com/v1"
```

### 启动

```bash
uv run uvicorn main:app --reload --port 8000
```

打开浏览器访问 `http://localhost:8000` 进入管理控制台。

### 验证

```bash
# 检查 Embedding 服务
curl -X POST "http://localhost:8000/validation/retrieval/embedding"

# 检查向量库
curl -X POST "http://localhost:8000/validation/retrieval/vectorstore"

# 检查检索链路
curl -X POST "http://localhost:8000/validation/retrieval/search"

# 全链路验证
curl -X POST "http://localhost:8000/validation/run"
```

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/ingress/upload` | 上传文件 |
| POST | `/knowledge/ingest` | 知识库摄入（解析 → 切分 → 索引） |
| GET | `/knowledge/status` | 知识库状态 |
| POST | `/qa/ask` | RAG 问答 |
| POST | `/validation/run` | 全链路验证 |
| GET | `/validation/status` | 系统状态快照 |
| POST | `/validation/scenario/knowledge-base` | 知识库场景验证 |
| POST | `/validation/scenario/qa` | QA 场景验证 |

## 使用示例

```python
# 上传 → 索引 → 问答
import httpx

# 1. 上传文档
with open("report.pdf", "rb") as f:
    resp = httpx.post("http://localhost:8000/ingress/upload", files={"file": f})
    file_info = resp.json()
    print(f"文件已上传: {file_info['filename']}")

# 2. 摄入知识库
resp = httpx.post("http://localhost:8000/knowledge/ingest", json={
    "file_path": "/path/to/parsed/document.md",
    "strategy": "recursive",
})
print(f"摄入结果: {resp.json()}")

# 3. 问答
resp = httpx.post("http://localhost:8000/qa/ask", json={
    "query": "BestRAG 支持哪些文档格式？",
    "top_k": 5,
})
answer = resp.json()
print(f"回答: {answer['answer']}")
print(f"来源: {len(answer['sources'])} 个文档")
```

## 配置参考

完整配置项请参考 `config.yaml`，所有配置均支持环境变量覆盖。

```yaml
retrieval:
  embedding_api_url: "http://localhost:8001/embed"
  embedding_dim: 1024
  vectorstore_type: "milvus"
  milvus_host: "localhost"
  milvus_port: 19530
  rerank_api_url: "http://localhost:8002/rerank"
  top_k: 10
  strategy: "hybrid"           # vector | bm25 | hybrid
  cache_enabled: true
  cache_backend: "redis"       # redis | memory
  index_version: "v1"          # 变更时缓存自动失效

generation:
  provider: "openai"
  model_name: "deepseek-chat"
  temperature: 0.2
  api_key: "${BESTRAG_LLM_API_KEY}"
  base_url: "https://api.deepseek.com/v1"
```

## 技术栈

| 类别 | 选择 |
|------|------|
| Web 框架 | FastAPI |
| 运行环境 | Python 3.12+ · uv |
| 向量数据库 | Milvus |
| Embedding 模型 | BGE-M3 / BAAI/bge-base-en-v1.5 |
| 检索算法 | 向量检索 · BM25 · 混合检索（加权融合） |
| 重排序 | BGE-Reranker |
| LLM 接入 | OpenAI 兼容协议（DeepSeek, OpenAI, 通义千问等） |
| 文档解析 | MarkItDown · OpenDataLoader |
| 缓存 | Redis （支持嵌入式和独立部署） |
| 前端 | 原生 HTML/CSS/JS 管理控制台 |

## Roadmap

### v0.1（当前 · alpha）
- [x] 核心应用容器与生命周期
- [x] 文档解析（Office / PDF / Markdown / 纯文本）
- [x] 文本清洗与策略切分
- [x] 向量检索 + BM25 + Hybrid 检索
- [x] BGE Embedding/Reranker 集成
- [x] OpenAI 兼容 LLM 接入
- [x] 两级检索缓存
- [x] 知识库管理 + RAG 问答 API
- [x] Web 管理控制台
- [x] 全链路验证中心

### v0.2（规划中）
- [ ] 流式输出（SSE / WebSocket）
- [ ] 多轮对话上下文管理
- [ ] 文档批量导入与增量更新
- [ ] 异步任务队列（文档处理非阻塞）
- [ ] 知识库多集合管理

### v0.3（规划中）
- [ ] 多租户与权限体系
- [ ] API Key 鉴权
- [ ] 日志与监控集成（Prometheus / Grafana）
- [ ] 性能优化与压力测试
- [ ] 更多向量数据库支持（Qdrant, Chroma）

### v0.4（规划中）
- [ ] Agent / 工具调用能力
- [ ] GraphRAG（知识图谱增强检索）
- [ ] 多模态文档支持（图片表格解析）
- [ ] 在线评估与 A/B 测试框架
- [ ] Helm Chart / Docker Compose 一键部署

## 开发

```bash
# 安装开发依赖
uv sync --group dev

# 运行测试
uv run pytest

# 代码风格
uv run ruff check .

# 新增依赖
uv add <package>
```

### 项目结构

```
BestRAG/
├── main.py                  # 应用入口（FastAPI）
├── config.yaml              # 全局配置
├── pyproject.toml           # 项目元数据与依赖
│
├── core/                    # 核心基础设施
│   ├── application/         # 应用容器与生命周期
│   ├── config.py            # 统一配置管理
│   ├── registry.py          # 服务注册中心
│   └── provider.py          # Provider 抽象基类
│
├── ingress/                 # 文件入口
├── document/                # 文档解析
├── processor/               # 清洗·切分·转换
├── indexing/                # 索引流程
├── retrieval/               # 检索·重排序·缓存
├── generation/              # 生成（LLM）
├── features/                # 对外功能 API
├── validation/              # 验证中心
│
├── static/console/          # Web 管理控制台
├── examples/                # 使用示例
└── tests/                   # 集成测试
```

## 许可

[MIT](LICENSE)

---

<p align="center">
  由 ❤️ 和 Python 驱动 · 问题或建议请提交 <a href="https://github.com/your-org/bestrag/issues">Issue</a>
</p>
