ADR-005-validation-module-design.md

目标：

建立独立 Validation 模块
不污染 main.py
对当前 Ingress + Document 链路进行验证
为未来 Processor / Retriever 提供统一验证框架

可直接交给 coding agent 实现。

# ADR-005 Validation Module Design

## Status

Proposed


## Module

BestRAG Validation Framework


## Version

v1.0


---

# 1. Overview


## 1.1 Background


目前 BestRAG 已完成：


Ingress Module

|

v

Document Module



其中：

Ingress:

- API Upload
- CLI Import
- Adapter
- InputFile Model
- IngressService


Document:

- Model
- Parser
- Dispatcher
- DocumentService


已经形成完整数据链路。


但是目前缺少：

- 自动化验证入口
- 模块级健康检查
- Pipeline 流程验证
- 统一测试输出


因此设计 Validation 模块。


---

# 2. Design Goal


Validation 模块目标：


## 2.1 验证模块完整性


例如：



Upload File

|

v

InputFile

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



验证整个流程是否正常。


---

## 2.2 不侵入业务代码


禁止：


DocumentService

|
+ validate()


禁止：


Parser

|
+ test()


原因：

业务模块不应该知道 Validation 存在。


---

## 2.3 main.py 保持纯净


main.py 只负责：


FastAPI

Dependency Injection

Router Register



禁止：


main.py

|
+ validation logic
+ test case
+ file processing


---

# 3. Architecture


新增模块：



BestRAG

├── validation

│
├── api

│ validation_api.py

│
├── model

│ validation_report.py

│
├── service

│ validation_service.py

│
└── checks

document_check.py


---

# 4. Responsibility


## 4.1 Validation API


职责：

提供 HTTP 验证入口。


例如：



POST

/validation/document



输入：

```json
{
    "file_path":"test.pdf"
}

输出：

{
    "status":"success",

    "document_id":"xxx",

    "parser":"PDFParser",

    "content_length":12345
}
5. Validation Service

核心组件：

ValidationService

职责：

编排验证流程。

例如：

validate_document(
    file_path
)

流程：

ValidationService


        |

        v


DocumentService


        |

        v


Document


        |

        v


ValidationReport

6. Validation 不实现业务逻辑

Validation 只能：

调用：

IngressService

DocumentService

Processor

收集：

result

error

duration

metadata


不能：

解析 PDF

读取 DOCX

生成 Chunk

7. Validation Report Model

新增：

validation/model/validation_report.py

使用：

Pydantic v2

定义：

class ValidationReport:


    status: str


    module: str


    duration_ms: float


    message: str | None


    details: dict

示例：

成功：

{
 "status":"success",

 "module":"document",

 "duration_ms":120,

 "details":{

    "parser":"PDFParser",

    "document_id":"uuid",

    "content_length":5000

 }
}

失败：

{
 "status":"failed",

 "module":"document",

 "message":"UnsupportedFileTypeError"
}
8. Document Validation Design
8.1 Validation Flow

验证：

file_path


 |

 v


DocumentService


 |

 v


DocumentDispatcher


 |

 v


Parser


 |

 v


Document

9. Document Check

新增：

validation/checks/document_check.py

负责：

Document 结果检查。

检查内容：

1. Document 是否生成

验证：

document is not None
2. ID 是否存在

检查：

document.id
3. Content 是否为空

检查：

len(document.content)
4. Metadata 是否正确

检查：

document.metadata.filename

document.metadata.file_type
10. Parser Validation

自动验证：

TXT

输入：

test.txt

验证：

TxtParser
Markdown

输入：

test.md

验证：

MarkdownParser
PDF

输入：

test.pdf

验证：

PDFParser
DOCX

输入：

test.docx

验证：

DocxParser
11. Error Validation

必须验证异常。

Unsupported File

例如：

test.exe

预期：

UnsupportedFileTypeError
File Not Found

例如：

not_exist.pdf

预期：

FileNotFoundError
Empty File

例如：

empty.txt

预期：

Document content empty
12. Dependency Injection

Validation 不创建业务对象。

错误：

ValidationService():

    DocumentService()


正确：

ValidationService(
    document_service
)

依赖：

Validation

      |

      v

DocumentService

13. API Integration

新增：

validation/api/validation_api.py

提供：

Document Validation
POST

/validation/document

请求：

{
 "file_path":"xxx.pdf"
}

响应：

ValidationReport
14. main.py Integration

只允许：

app.include_router(
    validation_router
)

禁止：

validate_document()
15. Implementation Order
Step 1

创建目录：

validation/

├── model

├── service

├── api

└── checks
Step 2

实现：

ValidationReport
Step 3

实现：

DocumentCheck
Step 4

实现：

ValidationService

依赖：

DocumentService
Step 5

实现：

validation_api.py
Step 6

main.py 注册 Router

16. Acceptance Criteria

完成后必须满足：

Document Pipeline
POST /validation/document

成功返回：

Document
+
Parser
+
Metadata
Parser Coverage

支持：

TXT

Markdown

PDF

DOCX
Exception Coverage

支持：

UnsupportedFileType

FileNotFound

EmptyDocument
Architecture

必须满足：

main.py

    |
    only router register


Validation

    |
    v

DocumentService

    |
    v

Document
17. Future Extension

未来扩展：

Processor Validation
/validation/processor

验证：

Document

 |

Chunk

Retriever Validation
/validation/retriever

验证：

Chunk

 |

Embedding

 |

Vector Search

Final Summary

Validation 模块定位：

验证系统

不是

业务系统

核心原则：

业务模块负责执行

Validation负责观察

最终形成：

Ingress

   |

Document

   |

Processor

   |

Retriever


        ↑

    Validation

END


---

这个 ADR 的实现完成后，你会得到一个很重要的能力：

以后每开发一个模块，不需要人工检查，而是：


新增模块
|
新增 validation check
|
自动验证整个链路