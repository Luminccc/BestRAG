# ADR-013: Retrieval Architecture Design

## Status

Accepted

## Date

2026-07-21

## Context

BestRAG 第一阶段已经完成：

- Ingress 模块
- Document 模块
- Processor 模块
    - Cleaner
    - Chunker
    - Transformer
- Validation Center

当前系统已经具备：


文件输入
|
Ingress
|
Document
|
Processor
|
Chunk


下一阶段需要实现 Retrieval 能力，使系统具备：


用户 Query

  |
  v

Embedding

  |
  v

Vector Store

  |
  v

Retrieval

  |
  v

Rerank

  |
  v

Context


Retrieval 是 RAG 系统中连接知识库和生成模型的核心模块。

因此需要设计一个：

- 可扩展
- 可替换
- Provider 无关
- 支持未来优化

的 Retrieval 架构。

---

# 1. Design Goal

## 1.1 V1目标

第一版本只实现基础能力：

### Embedding

支持：

- Document Chunk 向量化
- Query 向量化


### VectorStore

支持：

- 向量保存
- 相似度搜索


### Retrieval

支持：

- Query 检索
- Top-K 返回


### Rerank

支持：

- 基础二次排序接口


---

## 1.2 非目标

V1 不实现：

- Query Rewrite

- Hybrid Search

- Multi Vector Retrieval

- Cache

- Metadata Filtering Engine

- Knowledge Graph Retrieval

- Agent Retrieval


这些能力通过接口预留。

---

# 2. Architecture Overview



retrieval/

├── embedding/
│
├── vectorstore/
│
├── retrieval/
│
└── rerank/



四个模块职责：

|模块|职责|
|-|-|
|Embedding|文本转向量|
|VectorStore|向量存储和搜索|
|Retrieval|检索流程编排|
|Rerank|结果重新排序|

---

# 3. Embedding Module


## 3.1 Responsibility

Embedding 负责：


Text

↓

Vector



不负责：

- 存储
- 查询
- Ranking


---

# 3.2 Design


目录：


embedding/

├── base.py

├── model.py

├── service.py

└── providers/

└── bge.py


---

# 3.3 Interface


```python
class BaseEmbedding:

    def embed_text(
        self,
        text:str
    )->list[float]:
        pass


    def embed_documents(
        self,
        texts:list[str]
    )->list[list[float]]:
        pass
3.4 Provider

未来支持：

providers/

├── bge.py

├── openai.py

├── jina.py


调用方不依赖具体模型。

4. VectorStore Module
4.1 Responsibility

VectorStore负责：

保存Vector
删除Vector
相似度搜索

不负责：

Embedding
文本处理
4.2 Directory
vectorstore/

├── base.py

├── model.py

├── service.py

└── providers/


    ├── milvus.py

    ├── faiss.py

    └── chroma.py

4.3 Interface
class BaseVectorStore:


    def add(
        self,
        vectors,
        metadata
    ):
        pass



    def search(
        self,
        vector,
        top_k:int
    ):
        pass


    def delete(
        self,
        ids
    ):
        pass

4.4 Milvus Support

V1:

实现：

MilvusVectorStore


未来：

Milvus

↓

Chroma

↓

ElasticSearch


只替换 Provider。

5. Retrieval Module
5.1 Responsibility

Retrieval 是业务编排层。

负责：

Query

 ↓

Embedding

 ↓

Vector Search

 ↓

Result


5.2 Directory
retrieval/


├── model/

│
├── service.py

├── pipeline.py

└── strategy/


5.3 Retrieval Model

定义：

class RetrievalResult:


    chunk_id:str

    score:float

    content:str

    metadata:dict

5.4 Retrieval Service

接口：

class RetrievalService:


    def retrieve(
        self,
        query:str,
        top_k:int
    )->list[RetrievalResult]:

        pass

6. Rerank Module
6.1 Responsibility

Rerank负责：

Initial Result

      |

      v

Better Ranking


例如：

Vector Search:

100 chunks


Rerank:

100

↓

10

6.2 Directory
rerank/


├── base.py

├── service.py

└── providers/


    ├── bge.py

    └── jina.py

6.3 Interface
class BaseReranker:


    def rerank(
        self,
        query,
        documents
    ):

        pass

7. Complete Pipeline

V1流程：

User Query


   |

EmbeddingService


   |

VectorStore.search


   |

RetrievalResult


   |

(optional)

RerankService


   |

Context

8. Dependency Direction

必须保持：

RetrievalService

        |

        v


EmbeddingService


VectorStoreService


RerankService


禁止：

Embedding

调用

VectorStore


禁止模块互相依赖。

9. Future Extension
9.1 Cache

未来：

core/cache/


Redis

Memory Cache

Embedding Cache

Query Cache


Embedding:

text

 |

hash

 |

cache lookup

9.2 Hybrid Search

未来：

Vector Search

+

Keyword Search


扩展：

retrieval/strategy

├── vector.py

├── hybrid.py

9.3 Multi Model

未来：

Embedding Registry


bge

openai

jina

9.4 Async Processing

未来支持：

Embedding Queue

Batch Processing

10. Core Layer Integration

Retrieval需要Core提供：

core/


├── config

├── logger

├── registry

├── exception

└── cache(optional)


但是：

V1阶段：

只实现：

Config
Registry

其他按需增加。

11. Validation Integration

Retrieval必须接入：

Developer Validation Center

新增：

Validation

 |

 + validate_embedding

 + validate_vectorstore

 + validate_retrieval

 + validate_rerank


验证：

Embedding输出维度
VectorStore insert/search
Retrieval top-k
Rerank排序
12. Implementation Order

严格按照：

Step 1

Core基础能力

实现：

config
registry
Step 2

Embedding

实现：

BaseEmbedding
一个Provider
Step 3

VectorStore

实现：

BaseVectorStore
Milvus Adapter
Step 4

Retrieval

实现：

RetrievalService
Step 5

Rerank

实现：

BaseReranker
Step 6

Validation扩展

13. Decision Summary

采用：

Interface First
Provider Adapter Pattern
Service Orchestration
Core Support Layer

V1目标：

实现：

Document Chunk

        |

Embedding

        |

Milvus

        |

Retrieval

        |

Context


同时保证未来支持：

Cache
Hybrid Search
Multiple Models
Multiple Vector Database
Advanced Ranking



同时还有Retrieval 的 Validation 不应该只是测试 RetrievalService 是否返回结果，而应该继续沿用 Developer Validation Center 的理念：成为整个 Retrieval 子系统的可视化验证入口。

也就是说，之前：

Validation

├── Document Validation
├── Cleaner Validation
├── Chunker Validation
└── Transformer Validation

进入 Retrieval 后继续扩展：

Developer Validation Center

├── Ingress
├── Document
├── Processor
│
└── Retrieval
    │
    ├── Embedding Validation
    ├── VectorStore Validation
    ├── Retrieval Validation
    └── Rerank Validation
1. Retrieval Validation 的设计原则

遵循三个原则：

第一：验证能力，不验证实现

例如：

不要验证：

Milvus collection 是否存在

而验证：

VectorStore.search()
是否能够返回正确结果

因为未来可能替换：

Milvus
 ↓
Chroma
 ↓
FAISS

Validation 不应该改变。

第二：每个子模块独立验证

不要设计：

validate_retrieval()
里面全部跑完

因为如果失败，你不知道：

Embedding失败？
Milvus失败？
Retrieval逻辑失败？
Rerank失败？

所以：

Embedding
    |
    | validation

VectorStore
    |
    | validation

Retrieval
    |
    | validation

Rerank
    |
    | validation

2. Embedding Validation

目标：

确认模型服务正常。

新增：

validation/checks/embedding_check.py

验证：

Case 1

文本输入：

"BestRAG is a RAG framework"

检查：

返回：

{
 dimension:1024
}
Case 2

空文本：

输入：

""

预期：

failed
Case 3

批量Embedding

输入：

[
 "hello",
 "world"
]

检查：

数量一致。

结果：

Embedding Validation

✅ model loaded

✅ dimension correct

✅ batch embedding works

3. VectorStore Validation

这个最重要，因为第一次引入外部基础设施。

新增：

validation/checks/vectorstore_check.py

流程：

自动生成测试数据：

例如：

Chunk:

chunk1:

"Python programming language"


chunk2:

"Machine learning model"


然后：

Step 1

Embedding

生成：

vector1
vector2

Step 2

Insert:

VectorStore.add()
Step 3

Search:

query:

"python"


期待：

返回：

chunk1

验证：

insert success

search success

score exists

metadata exists

4. Retrieval Validation

这是核心。

新增：

validation/checks/retrieval_check.py

测试完整链路：

Query

 |

Embedding

 |

VectorStore

 |

RetrievalService

 |

Result


例如：

准备：

三个 Chunk：

A:

"Milvus is vector database"


B:

"Python language"


C:

"Apple company"


Query:

"What database stores vectors?"


期待：

Top1:

A

验证：

{
status:"success",

top_k:3,

result_count:3,

first_score:0.89
}
5. Rerank Validation

新增：

validation/checks/rerank_check.py

输入：

已经召回：

[
 chunkA score=0.7,
 chunkB score=0.8,
 chunkC score=0.5
]


Query:

"vector database"

验证：

Rerank后：

chunkA

应该提升


检查：

排序改变

score存在

top_n正确

6. API设计

保持现在风格：

validation/api/validation_api.py

新增：

Method	Path	功能
POST	/validation/retrieval/embedding	Embedding测试
POST	/validation/retrieval/vectorstore	VectorStore测试
POST	/validation/retrieval/search	Retrieval测试
POST	/validation/retrieval/rerank	Rerank测试
POST	/validation/retrieval/all	完整回归
7. 前端 Validation Center

增加：

Retrieval Section


🧠 Embedding

[Validate]


🗄 VectorStore

[Validate]


🔎 Retrieval

[Validate]


📊 Rerank

[Validate]


🚀 Full Retrieval Regression

[Run]

8. 全量回归流程

最终：

点击：

Run Retrieval Regression

自动：

Embedding

    ↓

VectorStore

    ↓

Retrieval

    ↓

Rerank


输出：

Retrieval Regression Report


Embedding

PASS


VectorStore

PASS


Retrieval

PASS


Rerank

PASS


Total:

4/4
我的建议

现在不要急着实现 Validation。

正确顺序应该：

ADR-013 Retrieval Design

        ↓

实现 Core 基础能力

        ↓

Embedding

        ↓

Validation Embedding

        ↓

VectorStore

        ↓

Validation VectorStore

        ↓

Retrieval

        ↓

Validation Retrieval

        ↓

Rerank

        ↓

Validation Rerank

也就是说：

Validation 要跟随模块开发，而不是最后补。

这和之前 Cleaner、Chunker、Transformer 的开发方式保持一致，也是 BestRAG 目前最稳定的开发节奏。