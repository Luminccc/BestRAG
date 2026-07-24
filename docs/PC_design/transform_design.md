ADR-011-processor-transformer-design.md

设计原则：

Transformer 第一阶段只负责 Document/Chunk 数据结构规范化与溯源信息增强
不包含 AI 摘要、关键词、标签生成
保持无副作用、可测试、可扩展
为未来 Metadata Enhancement 留接口
# ADR-011 Processor Transformer Design

## Status

Proposed


## Module

Processor - Transformer


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

Processor

|

+-------------+

|             |

Cleaner Chunker



当前流程：


Raw File

|

v

Document

|

v

Cleaner

|

v

Chunk[]



Chunk 已经完成：

- Chunk Model
- Fixed Strategy
- Recursive Strategy


下一阶段需要增加 Transformer。


---

# 2. Transformer Responsibility


Transformer 负责：


Processed Data Normalization



主要目标：

- 数据结构统一
- 数据溯源信息补充
- Schema规范化
- 为后续RAG流程提供标准数据


---

# 3. Design Principles


## 3.1 Single Responsibility


Transformer只负责：


数据转换



不负责：

- 文件读取
- Chunk切分
- Embedding
- Retrieval
- AI生成内容


---

## 3.2 No Side Effect


Transformer：

输入：


Document / Chunk



输出：


Document / Chunk



不直接：

- 写数据库
- 调用外部API
- 修改文件


---

## 3.3 Extensible


未来支持：


Metadata Enhancement

Summary Generation

Keyword Extraction

Tag Generation



但是第一阶段不实现。


---

# 4. Transformer Scope


## Phase 1 (Current)


实现：

### 1. Schema Normalization

统一数据结构。


### 2. Data Lineage

增加来源信息。


### 3. Metadata Standardization


规范：


Document.metadata

Chunk.metadata



---

# 5. Data Lineage Design


## Purpose


保证每个 Chunk 可以追溯到：


Chunk

|

v

Document

|

v

Original File



---

# 6. Lineage Metadata


Document:

```json
{
 "source_file":"example.pdf",

 "document_id":"xxx",

 "created_time":"xxx"
}

Chunk:

{
 "document_id":"xxx",

 "chunk_index":1
}
7. JSON Schema Normalization

Transformer负责：

将不同来源的数据：

PDF

DOCX

Markdown

TXT

统一转换为标准结构。

8. Standard Schema

Document:

{
"id":"uuid",

"content":"text",

"metadata":{

 "filename":"",

 "file_type":"",

 "source":""

}
}

Chunk:

{
"id":"uuid",

"document_id":"uuid",

"content":"text",

"metadata":{

 "chunk_index":0

}
}
9. Content Enhancement Boundary
Not included in Phase 1

以下能力暂不实现：

Summary

Keywords

Tags

Entity Extraction

原因：

这些通常需要：

LLM
NLP Model
Embedding

属于后续 Enhancement Layer。

10. Future Extension

未来：

Transformer


    |

    +----------------+

    |                |

 Schema Transformer


 Metadata Enhancer


 AI Content Enhancer

11. Directory Design

结构：

processor/


├── cleaner/


├── chunker/


├── transformer/

│
│── base.py

│
│── schema_transformer.py

│
│── __init__.py


└── service/

12. BaseTransformer Interface

文件：

processor/transformer/base.py

接口：

class BaseTransformer:


    def transform(
        self,
        data
    ):
        pass
13. SchemaTransformer

文件：

schema_transformer.py

职责：

Document / Chunk Schema统一。

接口：

class SchemaTransformer(BaseTransformer):


    def transform(
        self,
        document
    ):
        ...
14. TransformerService

说明：

Service层负责流程编排。

调用：

Document

    |

    v

TransformerService

    |

    v

SchemaTransformer

    |

    v

Document

接口：

transform(
    document:Document
)->Document
15. Service Responsibility

TransformerService负责：

调用 Transformer
管理执行顺序
统一异常处理

不负责：

具体转换规则
16. Validation Integration

增加：

validation/checks/transformer_check.py
17. Validation API

新增：

POST

/validation/processor/transformer

请求：

{
 "file_path":"test.pdf"
}

流程：

file_path

 |

 v

DocumentService

 |

 v

Document

 |

 v

TransformerService

 |

 v

ValidationReport
18. Validation Rules

检查：

Schema Valid

验证：

Document字段完整
Lineage Exists

检查：

document_id

filename

file_type
Chunk Relation

如果输入Chunk：

检查：

chunk.document_id

exists
19. Developer Validation Center

新增：

Processor Validation


[Cleaner]

[Chunker]

[Transformer]


Transformer结果展示：

Document ID

Source File

Schema Status

Metadata

20. Implementation Order
Step 1

创建：

processor/transformer
Step 2

实现：

BaseTransformer
Step 3

实现：

SchemaTransformer
Step 4

实现：

TransformerService
Step 5

扩展：

Validation API
Step 6

更新：

Developer Validation Center
21. Acceptance Criteria

完成后：

Transformer支持：

Document

    |

    v

Schema Normalization

    |

    v

Document

并保证：

数据结构统一
数据来源可追踪
Chunk关联关系保留
无AI生成逻辑
Final Architecture
Document


    |

    v


Cleaner


    |

    v


Chunker


    |

    v


Transformer


    |

    v


Embedding


    |

    v


VectorStore

Summary

Transformer第一阶段定位：

数据标准化层

核心能力：

Schema Normalization

+

Data Lineage

未来扩展：

Summary

Keywords

Tags

Semantic Metadata

遵循：

简单实现

明确边界

持续扩展

END


---

补充建议：  
这里我刻意把 **Transformer 放在 Chunker 后面**，原因是未来你的摘要、关键词、标签等增强，大概率最终服务对象不是原始 Document，而是 **Chunk 级别内容**。

所以未来演进会比较自然：


Document
↓
Cleaner
↓
Chunker
↓
Transformer
↓
Chunk(metadata增强)
↓
Embedding


这条链路会更符合 RAG 系统的实际工程结构。