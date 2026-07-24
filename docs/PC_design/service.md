# ADR-012 Processor Pipeline Design

## Status

Proposed


## Module

Processor - Pipeline Service


## Version

v1.0


---

# 1. Overview


## 1.1 Background


当前 BestRAG 已完成 Processor 三个核心子模块：


processor/

├── cleaner/

├── chunker/

└── transformer/



各模块能力：

|模块|状态|职责|
|-|-|-|
|Cleaner|✅|文本清洗|
|Chunker|✅|文本切分|
|Transformer|✅|Schema标准化与数据溯源|


当前调用方式：


Document

|

+--> Cleaner

+--> ChunkService

+--> TransformerService


三个模块已经具备能力，但缺少统一编排入口。


因此升级：


ProcessorService


作为 Processor Pipeline 的统一入口。


---

# 2. Design Goal


建立：


Document

|

v

ProcessorService

|

v

Processed Result



统一负责：

- Processor执行顺序
- 子模块调用
- 参数传递
- 异常管理


---

# 3. Design Principles


## 3.1 Single Entry Point


外部调用只依赖：


ProcessorService



不直接调用：


Cleaner

ChunkService

TransformerService



---

## 3.2 Pipeline Extensibility


未来增加：


OCR Processor

Metadata Processor

Quality Checker

Language Detector



只需要加入 Pipeline。


不修改调用方。


---

## 3.3 Module Isolation


ProcessorService：

负责：


什么时候调用



子模块：

负责：


如何处理



---

# 4. Pipeline Flow


标准流程：



Document

|

v

Cleaner

|

v

Clean Document

|

v

Chunker

|

v

Chunk[]

|

v

Transformer

|

v

Processed Result



---

# 5. Execution Order


固定顺序：

## Step 1 Cleaner


原因：

Chunk需要基于干净文本。



Raw Document

↓

Clean Document



---

## Step 2 Chunker


输入：


Clean Document



输出：


Chunk[]



---

## Step 3 Transformer


输入：


Document / Chunk



输出：


标准化数据



---

# 6. ProcessorService Design


## Location


保持：


processor/service/



文件：


processor/service/processor_service.py



---

# 7. Interface


```python
class ProcessorService:


    def process(
        self,
        document: Document,
        strategy: str = "recursive"
    ):
        pass

参数：

参数	说明
document	输入Document
strategy	Chunk策略
8. Dependency Injection

ProcessorService依赖：

ProcessorService


    |

    +--> Cleaner


    |

    +--> ChunkService


    |

    +--> TransformerService


示例：

ProcessorService(
    cleaner,
    chunk_service,
    transformer_service
)
9. Process Result Design
MVP Decision

新增：

ProcessedDocument

位置：

processor/model/

原因：

Processor输出已经不再是单一Document。

10. ProcessedDocument Model

结构：

class ProcessedDocument:

    document: Document

    chunks: list[Chunk]
11. Why Not Return list[Chunk]

如果直接返回：

Chunk[]

会丢失：

原始Document信息
metadata
lineage

未来：

Embedding、Audit、Debug 都需要Document。

因此保留：

Document + Chunk[]
12. Pipeline Example

输入：

Document

content:

"large text..."

执行：

Cleaner

↓

content normalized


↓

Chunker

↓

[
 Chunk1,
 Chunk2
]


↓

Transformer

↓

ProcessedDocument

{
 document,
 chunks
}

13. Exception Handling

ProcessorService负责统一异常。

例如：

CleanerError

ChunkError

TransformerError

统一转换：

ProcessorError
14. Validation Integration

新增：

validation/checks/pipeline_check.py
15. Pipeline Validation API

新增：

POST

/validation/processor/pipeline

请求：

{
 "file_path":"test.pdf",

 "strategy":"recursive"
}
16. Validation Flow
file_path


↓

DocumentService


↓

Document


↓

ProcessorService


↓

ProcessedDocument


↓

ValidationReport
17. Validation Rules

检查：

Document Exists
processed.document != None
Chunk Exists
len(processed.chunks)>0
Chunk Relation

检查：

chunk.document_id

=

document.id
Metadata

检查：

Transformer metadata exists
18. Developer Validation Center

增加：

Processor Pipeline

页面：

Processor


[Validate Cleaner]


[Validate Chunker]


[Validate Transformer]


[Run Pipeline]


Pipeline结果：

Document

Cleaner Status

Chunk Count

Transformer Status

Duration
19. Implementation Order
Step 1

创建：

processor/model/

实现：

ProcessedDocument
Step 2

升级：

ProcessorService

加入：

Cleaner

ChunkService

TransformerService
Step 3

更新：

main.py

注入：

ProcessorService
Step 4

扩展：

ValidationService

新增：

validate_pipeline()
Step 5

更新：

Developer Validation Center

增加：

Pipeline Button
20. Acceptance Criteria

完成后：

统一调用：

Document

↓

ProcessorService

↓

ProcessedDocument

支持：

Cleaner

+

Chunker

+

Transformer

并且：

模块之间低耦合
新增Processor步骤无需修改调用方
Validation可以验证完整Pipeline
Final Architecture
Ingress

   |

   v

DocumentService

   |

   v

Document


   |

   v


ProcessorService


   |

   +----------+

   |          |

Cleaner    Chunker

              |

              v

           Chunk[]


              |

              v

        Transformer


              |

              v


ProcessedDocument


              |

              v


Embedding


              |

              v


VectorStore

Summary

ProcessorService升级目标：

从：

Cleaner调用器

变成：

RAG数据处理流水线入口

核心价值：

统一入口

模块解耦

可扩展Pipeline

持续Validation