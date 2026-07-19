

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



③ model

这是我认为：

整个系统最重要的目录。

因为：

整个BestRAG：

以后：

所有模块：

只认识：

Document。

我建议：

这里不要急着写。

而是：

好好设计。

例如：

Document

Section

Paragraph

Table

Image

Metadata

以后：

Chunk：

Retriever：

Agent：

全部：

依赖：

这里。

千万不要：

Retriever：

自己：

定义：

Document。

④ processor

注意：

Processor：

处理的是：

Document。

不是：

File。

例如：

Document

↓

Normalize

↓

Metadata

↓

Table Fix

↓

Image Process

↓

Summary

↓

Keyword

↓

Processed Document

Processor：

以后：

越来越大。

但是：

永远：

不要：

解析PDF。

例如：

Normalize：

可以：

统一标题

统一换行

统一编码

统一图片引用

Processor：

建议：

Pipeline。

例如：

processor/

    normalize/

    cleaner/

    metadata/

    keyword/

    summary/

    image/

    table/
⑤ application

这里很多人容易误解。

它不是：

业务逻辑。

它是：

Use Case。

例如：

ImportDocument

↓

Dispatcher

↓

Processor

↓

Save

Application：

负责：

调用：

多个领域服务。

而不是：

实现：

算法。

例如：

ImportDocumentService

里面：

只有：

流程。

没有：

Parser。

第三层 retrieval

这里：

已经进入：

RAG。

chunk

唯一职责：

Document

↓

Chunks

千万不要：

Embedding。

Chunk：

只关心：

如何：

切。

embedding

唯一职责：

Chunk

↓

Vector

不要：

存Milvus。

vectordb

唯一职责：

Save

Delete

Search

以后：

Milvus

FAISS

PGVector

全部：

Adapter。

retriever

Retriever：

不要：

Embedding。

Retriever：

负责：

Query

↓

Hybrid Search

↓

Candidate

例如：

以后：

BM25

Vector

Metadata

都在：

这里。

rerank

唯一职责：

Candidate

↓

TopK

这里：

以后：

接：

BGE-Reranker。

context

这是我今天最想加的。

为什么？

因为：

Agent：

真正：

拿到的：

不是：

Chunk。

而是：

Context。

例如：

Chunk1

Chunk2

Chunk3

↓

Merge

↓

Window

↓

Prompt Context

以后：

这里：

可以：

加入：

Context Compression

Lost in Middle

Long Context
整个数据流

我建议以后永远遵守：

External

↓

Ingress

↓

InputFile

↓

Dispatcher

↓

Document

↓

Processor

↓

Processed Document

↓

Chunk

↓

Embedding

↓

VectorDB

────────────────────────────

Query

↓

Retriever

↓

Rerank

↓

Context

↓

LLM

注意：

上下：

两条流程。

一个：

Build。

一个：

Search。

千万不要：

混。

我建议整个BestRAG建立三个核心对象（Core Object）

这是我认为最重要的一点，也是整个架构以后能否长期演进的关键。

整个系统不要到处传字符串、字典或第三方对象，而是始终围绕三个核心对象：

核心对象	生命周期	谁创建	谁消费
InputFile	接入阶段	ingress	document.dispatcher
Document	文档阶段	parser（通过 Dispatcher）	processor、chunk
Chunk	检索阶段	chunk	embedding、retriever

整个系统的数据流就变成：

InputFile
      │
      ▼
Document
      │
      ▼
Chunk
      │
      ▼
Vector

这样以后即使你替换 MarkItDown、OpenDataLoader、Milvus，甚至增加 Confluence、GitHub、Jira 等新的接入方式，这三个核心对象都不会变化。

我认为，这三个对象会成为 BestRAG 的"领域语言（Ubiquitous Language）"，也是整个框架最值得长期稳定维护的核心。 这也是我建议我们下一步重点设计的内容——先把 InputFile、Document、Chunk 三个领域模型设计好，再开始写 Dispatcher。