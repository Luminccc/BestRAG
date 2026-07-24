ADR-008-document-service-design.md

这个 ADR 主要解决一个问题：

DocumentService 到底负责什么，避免 Service 变成业务大杂烩。

核心定位：

Service = Document 流程编排层

而不是：

Service = 所有逻辑集中地
# ADR-008 Document Service Design

## Status

Proposed


## Module

BestRAG Document Service Module


## Version

v1.0


---

# 1. Overview


## 1.1 Module Position


`document/service` 是 Document 模块的业务编排层。


它负责：

> 串联 Document 内部各组件，完成从文件到 Document 对象的完整流程。


整体架构：


Ingress

|

v

DocumentService

|

+----------------+

| |

Dispatcher Metadata

|

v

Parser

|

v

Document Model

|

v

Processor



---

# 2. Responsibility


## 2.1 DocumentService Does


DocumentService 负责：


### 1. 接收 Document 创建请求


例如：

```python
create_document(file_path)
2. 调用 Dispatcher

流程：

file_path

    |

    v

Dispatcher

    |

    v

Parser
3. 返回统一 Document

输出：

Document
4. 流程异常管理

例如：

ParserError
UnsupportedFileTypeError

统一向上层传递。

3. DocumentService Does Not Do
3.1 不负责解析

错误：

DocumentService.parse_pdf()

解析属于：

document/parser
3.2 不负责选择 Parser

错误：

if file_type=="pdf":

    PDFParser()

选择属于：

document/dispatcher
3.3 不负责清洗

错误：

DocumentService.clean()

属于：

processor/cleaner
3.4 不负责切片

属于：

processor/chunker
3.5 不负责 Embedding

属于：

retriever/embedding
4. Design Principle
4.1 Service Orchestration Only

核心原则：

Service负责调用

组件负责实现

例如：

正确：

document = dispatcher.dispatch(
    file_path
)

错误：

text = extract_pdf(file)

chunk(text)

embed(text)
5. Input Design
Decision

MVP 输入：

file_path: str

原因：

保持简单。

调用链：

API

 |

 v

DocumentService

 |

 v

Dispatcher

未来可以扩展：

DocumentCreateRequest

例如：

class DocumentCreateRequest:

    file_path:str

    source:str

    owner:str

6. Output Design

输出：

Document

示例：

document = service.create_document(
    file_path
)

返回：

Document(

    id="uuid",

    content="xxx",

    metadata={}

)
7. Directory Structure

设计：

document

└── service

    ├── document_service.py

    ├── exceptions.py

    └── __init__.py
8. DocumentService Design
8.1 Class Definition
class DocumentService:


    def __init__(
        self,
        dispatcher: DocumentDispatcher
    ):

        self.dispatcher = dispatcher
8.2 Main Method
def create_document(
    self,
    file_path:str
)->Document:


    document = self.dispatcher.dispatch(
        file_path
    )


    return document
9. Dependency Direction

必须保持：

service

    |

    v

dispatcher

    |

    v

parser

    |

    v

model

禁止：

parser

    |

    v

service

原因：

避免循环依赖。

10. Metadata Handling
Decision

DocumentService 是 Metadata 增强的预留位置。

但是 MVP 阶段：

只负责：

filename
file_type

由 Parser 创建。

不负责：

keywords

summary

tags

这些属于：

processor/transformer

未来：

DocumentService 可以增加：

document.metadata.source

例如：

upload

crawler

api
11. Error Handling

Service 不重新定义底层异常。

例如：

Dispatcher:

UnsupportedFileTypeError

Parser:

ParserError

直接向上传递。

未来 API 层可以转换：

例如：

ParserError

    |

    v

HTTP 400
12. Lifecycle

完整流程：

create_document()


        |

        v


DocumentService


        |

        v


Dispatcher


        |

        v


Parser


        |

        v


Document


        |

        v


return
13. Implementation Steps
Step 1

创建：

document/service/exceptions.py

目前为空或预留。

Step 2

创建：

document/service/document_service.py

实现：

DocumentService
Step 3

实现依赖注入：

dispatcher = DocumentDispatcher()

service = DocumentService(
    dispatcher
)
Step 4

创建：

document/service/__init__.py

统一导出。

14. Acceptance Criteria

完成后必须满足：

1

调用 Service 可以创建 Document

例如：

service.create_document(
    "test.pdf"
)

返回：

Document
2

Service 不包含解析代码

禁止：

fitz.open()

docx.Document()

open()
3

Service 不包含 Processor 逻辑

禁止：

chunk()

clean()

embed()
4

依赖方向正确

必须：

Service

 |

 v

Dispatcher

 |

 v

Parser

 |

 v

Model
15. Final Architecture

Document 模块最终结构：

document


├── model

│
│   Document

│
├── parser

│
│   BaseParser

│   PDFParser

│   DocxParser

│
├── dispatcher

│
│   Parser Registry

│   Parser Selection

│
└── service

    DocumentService

    Workflow Orchestration
Summary

DocumentService 的核心定位：

负责流程

不负责实现

最终原则：

Model
    定义数据

Parser
    转换数据

Dispatcher
    选择转换器

Service
    串联流程

END


---

实现顺序建议：

当前 Document 模块：

```text
model        ✅
parser       ✅
dispatcher   ✅
service      ⏳

完成 Service 后，Document 模块就形成完整闭环：

API / CLI

   |

   v

DocumentService

   |

   v

Dispatcher

   |

   v

Parser

   |

   v

Document

   |

   v

Processor

之后就可以进入下一大模块：
