ADR-010-processor-chunker-design.md

设计重点：

Chunk 作为独立领域模型，放在 processor/chunker 下
支持多种 Chunk 策略扩展
第一版实现 Fixed + Recursive
预留 Semantic / Heading / Hierarchical 扩展能力
不影响后续 Embedding、VectorStore、Retriever

可以直接交给 coding agent。

# ADR-010 Processor Chunker Design

## Status

Proposed


## Module

Processor - Chunker


## Version

v1.0


---

# 1. Overview


## 1.1 Background


当前 BestRAG 已完成：



Ingress

|

v

Document

|

v

Cleaner



Cleaner 已完成：

- 空白处理
- 换行规范化
- 控制字符清理


当前数据：


Document

{

id,

content,

metadata

}



但是 Document 仍然是完整文本。

为了支持：

- Embedding
- Vector Search
- BM25
- Hybrid Retrieval
- Reranker


需要将 Document 转换为 Chunk。


---

# 2. Chunker Responsibility


Chunker 负责：



Clean Document

    |

    v

Chunk[]



核心职责：

- 文本切分
- 保留上下文关系
- 生成 Chunk Metadata


---

# 3. Design Goal


## 3.1 Extensibility


第一版不追求实现所有策略。

但是架构必须支持：



Fixed Chunk

Recursive Chunk

Heading Chunk

Semantic Chunk

Custom Chunk



未来新增策略：

不修改：

- Chunk Model
- ChunkService
- Embedding
- VectorStore


---

# 4. Core Design Principles


## Principle 1

统一 Chunk 数据模型


所有策略输出：



Chunk[]



例如：



FixedChunkStrategy

    |

    v

Chunk[]

SemanticChunkStrategy

    |

    v

Chunk[]



---

## Principle 2

Strategy Pattern


禁止：


```python
if strategy=="fixed":

elif strategy=="semantic":

elif strategy=="heading":


原因：

随着策略增加：

代码不可维护。

采用：

BaseChunkStrategy

        |

        +------------+

        |            |

 FixedStrategy  RecursiveStrategy

Principle 3

Chunker 与策略解耦

调用方：

ChunkService

        |

        v

ChunkStrategy


不知道内部如何切分。

5. Chunk Model Design
5.1 Location

Chunk 不属于：

processor/model

原因：

Chunk 是 Chunker 领域对象。

位置：

processor/

└── chunker/

    └── model/

        └── chunk.py

5.2 Chunk Entity

定义：

class Chunk:

    id: str

    document_id: str

    content: str

    index: int

    metadata: dict
5.3 Field Description
字段	说明
id	Chunk唯一ID
document_id	来源Document
content	Chunk文本
index	顺序编号
metadata	扩展信息
6. Chunk Metadata

metadata 用于未来扩展。

例如：

{
 "strategy":"recursive",

 "start":100,

 "end":500,

 "page":2,

 "heading":"Introduction"
}
7. Directory Design

最终结构：

processor/


├── cleaner/

│
├── chunker/

│   │
│   ├── model/

│   │   └── chunk.py

│   │
│   ├── strategy/

│   │   ├── base.py

│   │   ├── fixed.py

│   │   └── recursive.py

│   │
│   ├── service/

│   │   └── chunk_service.py

│   │
│   └── __init__.py

8. Strategy Interface
Base Strategy

文件：

chunker/strategy/base.py

接口：

class BaseChunkStrategy:


    def split(
        self,
        text:str
    )->list[Chunk]:

        pass

9. Fixed Chunk Strategy
Purpose

按照固定长度切分。

例如：

chunk_size=500

输入：

1000 chars

输出：

Chunk1 0-500

Chunk2 500-1000

Parameters

支持：

chunk_size

overlap


例如：

size=500

overlap=50

10. Recursive Chunk Strategy
Purpose

根据文本结构递归切分。

优先级：

Paragraph

        ↓

Sentence

        ↓

Character


例如：

large text


|

paragraph split


|

sentence split

11. Future Strategies
Heading Strategy

适用于：

Markdown

技术文档

依据：

#

##

###
Semantic Strategy

适用于：

知识库问答

依据：

Embedding similarity

例如：

sentence A

sentence B


similarity > threshold


merge

12. ChunkService

职责：

统一调用入口。

接口：

chunk(

 document:Document,

 strategy:str

)->list[Chunk]


调用流程：

Document


   |

   v


ChunkService


   |

   v


Strategy Selector


   |

   v


Chunk Strategy


   |

   v


Chunk[]

13. Strategy Registry

为了扩展：

增加 Registry。

例如：

CHUNK_STRATEGIES={


"fixed":FixedChunkStrategy,


"recursive":RecursiveChunkStrategy


}


未来：

新增：

"semantic":SemanticChunkStrategy

即可。

14. Validation Integration

Chunk 完成后加入 Validation。

新增：

validation/checks/chunk_check.py
15. Chunk Validation API

新增：

POST

/validation/processor/chunk

请求：

{
 "file_path":"test.pdf",

 "strategy":"recursive"
}
16. Validation Rules

检查：

Chunk Count
len(chunks)>0
Content

每个 Chunk：

content != ""
Metadata

检查：

document_id exists
Length

记录：

{
"chunk_count":20,

"avg_length":400,

"max_length":500
}
17. Developer Validation Center

新增：

Processor Validation

页面：

Processor


[Validate Cleaner]


[Validate Chunker]


Strategy:

<select>

fixed

recursive


</select>


Result

18. Implementation Order
Step 1

创建：

chunker/model

实现：

Chunk
Step 2

实现：

BaseChunkStrategy
Step 3

实现：

FixedChunkStrategy
Step 4

实现：

RecursiveChunkStrategy
Step 5

实现：

ChunkService
Step 6

增加：

Validation API
Step 7

增加：

Developer Validation Center

19. Acceptance Criteria

完成后：

Model

支持：

Chunk
Strategy

支持：

fixed

recursive
Extension

未来支持：

semantic

heading

custom

无需修改：

Chunk Model

Embedding

VectorStore

Retriever

Validation

支持：

POST /validation/processor/chunk

返回：

{
"status":"success",

"module":"chunker",

"details":{

"strategy":"recursive",

"chunk_count":20,

"avg_length":400

}

}
Final Architecture
Document


    |

    v


Cleaner


    |

    v


Clean Document


    |

    v


ChunkService


    |

    +----------------+

    |                |

 Fixed Strategy   Recursive Strategy


    |

    v


Chunk[]


    |

    v


Embedding


    |

    v


VectorStore

Summary

Chunker设计原则：

统一模型

策略可插拔

服务统一入口

验证持续集成

第一版：

实现：

Chunk Model

Fixed Chunk

Recursive Chunk

ChunkService

Validation

为未来：

Semantic Chunk

Heading Chunk

Adaptive Chunk


保留扩展能力。

END



---

补充说明：这个 ADR 里我特意把 **Chunk Model 放到了 `processor/chunker/model`，没有放 `processor/model`**，因为 Chunk 会成为后续整个 RAG 系统的核心实体，它属于 Chunking 领域，而不是 Processor 全局公共模型。这样后续 Embedding、VectorStore、Retriever 都可以稳定依赖 Chunk。
语音聊天已结束
8分钟29秒