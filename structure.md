

技术选型
1.前置处理

文档切分这里选用  Markitdown() + Opendataloader(Hybrid模式)


                    企业知识库

                       │
                 Document Upload
                       │



                       ▼
              Document Dispatch Center（文档调度中心）
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
   MarkItDown                 OpenDataLoader
 (Office Family)             (PDF Family)
        │                             │
        │                    Local + Hybrid
        │                    （内部自动选择）
        │
        └──────────────┬──────────────┘
                       ▼
            Unified Document Model
                       │
                 Document Normalize
                       │
                 Semantic Chunk
                       │
                  Embedding
                       │
                     Milvus
                       │
             Hybrid Retrieval
                       │
                   Reranker
                       │
                   Agent / LLM
本项目将模仿RAG-anything 做一个RAG的框架

workspace/ 管理文件生命全周期
static/ 管理webui 文件目录
 现在

  一套依赖声明 + uv 自动管理：

    pyproject.toml      ← 依赖清单（唯一真相来源）
         │
    uv sync             ← 自动创建 .venv、锁定版本
         │
    uv run main.py      ← 在 .venv 中运行
         │
    uv add <package>    ← 新增依赖

  常用命令

  ┌─────────────────┬───────────────────────┐
  │      命令       │         说明          │
  ├─────────────────┼───────────────────────┤
  │ uv sync         │ 安装/同步所有依赖     │
  ├─────────────────┼───────────────────────┤
  │ uv run main:app │ 启动服务器            │
  ├─────────────────┼───────────────────────┤
  │ uv add xxx      │ 新增依赖              │
  ├─────────────────┼───────────────────────┤
  │ uv lock         │ 更新 uv.lock 锁定文件 │
  ├─────────────────┼───────────────────────┤
  │ uv tree         │ 查看依赖树            │
  └─────────────────┴───────────────────────┘

  新机器上的首次启动

  git clone <repo>
  cd BestRAG
  uv sync
  uv run uvicorn main:app --reload --port 8888

  不需要手动装 Python 包，uv sync 全部搞定。

embedding 模型选择bgem3 8001  bge-rerank 8002 虚拟环境 source bge-env/bin/activate
Milvus 19530 attu 8000
cd ~/ai
./scripts/start_all.sh
./scripts/stop_all.sh   

attu 8000
bgem3 8001
bge-rerank 8002
Milvus 19530