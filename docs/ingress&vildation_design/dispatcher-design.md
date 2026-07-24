

定位：给 coding agent 实现 `document/dispatcher` 使用。

重点明确：

- Dispatcher 职责边界
- 输入输出设计
- Parser 注册机制
- 文件类型识别
- Metadata 处理
- 异常设计
- 实现步骤

------

```
# ADR-007 Document Dispatcher Design

## Status

Proposed


## Module

BestRAG Document Dispatcher Module


## Version

v1.0


---

# 1. Overview


## 1.1 Module Position


`document/dispatcher` 是 Document 模块中的调度层。


它负责：

> 根据输入文件类型，选择正确的 Parser，并执行解析流程。


整体链路：
```

User Upload File

```
    |

    v
```

Ingress

```
    |

    v
```

Document Dispatcher

```
    |

    v
```

Document Parser

```
    |

    v
```

Document Model

```
    |

    v
```

Processor

```
---

# 2. Responsibility


## 2.1 Dispatcher Does


Dispatcher 负责：


1. 文件类型识别

2. Parser 查找

3. Parser 调用

4. 返回 Document


即：
```

File

|

v

Dispatcher

|

v

Parser

|

v

Document

```
---

## 2.2 Dispatcher Does Not Do


Dispatcher 不负责：


## 文件内容解析


例如：

​```text
PDF文本提取
DOCX读取
Markdown解析
```

属于：

```
document/parser
```

------

## 文档清洗

属于：

```
processor/cleaner
```

------

## 文档切片

属于：

```
processor/chunker
```

------

## Embedding

属于：

```
retriever/embedding
```

------

## Vector Storage

属于：

```
retriever/vector_store
```

------

# 3. Design Principle

## 3.1 Single Responsibility

Dispatcher 只做：

```
选择 Parser
```

禁止：

```
class Dispatcher:


    def parse_pdf():

        pass


    def clean():

        pass
```

------

# 4. Input Design

## Decision

Dispatcher 输入：

```
file_path: str
```

原因：

保持 Document 模块独立。

不直接依赖：

```
Ingress.InputFile
```

避免：

```
document

    |

    强依赖

    |

ingress
```

------

# 5. Output Design

Dispatcher 输出：

```
Document
```

流程：

```
document = dispatcher.dispatch(
    file_path
)
```

返回：

```
Document(
    id="xxx",

    content="xxx",

    metadata={}
)
```

------

# 6. Directory Structure

设计：

```
document

└── dispatcher

    ├── dispatcher.py

    ├── registry.py

    └── exceptions.py
```

------

# 7. Parser Registry Design

## 7.1 Purpose

Registry 保存：

```
文件类型

     |

     v

Parser Class
```

映射关系。

------

## 7.2 Implementation

采用：

```
Static Registry
```

MVP 阶段不使用动态插件。

原因：

- 简单
- 可维护
- 易调试

------

示例：

```
PARSER_REGISTRY = {

    "pdf": PDFParser,

    "docx": DocxParser,

    "markdown": MarkdownParser,

    "txt": TXTParser

}
```

------

# 8. Parser Registration

推荐方式：

集中注册：

```
from document.parser import (
    PDFParser,
    DocxParser,
    MarkdownParser,
    TXTParser
)


PARSER_REGISTRY = {

    "pdf": PDFParser,

    "docx": DocxParser,

    "markdown": MarkdownParser,

    "txt": TXTParser

}
```

------

不要：

每个 Parser 自己修改 Dispatcher。

避免：

```
Parser

 |

修改

 |

Dispatcher
```

产生循环依赖。

------

# 9. File Type Detection

## Decision

MVP 使用：

```
文件扩展名
```

例如：

```
test.pdf

      |

      v

pdf

      |

      v

PDFParser
```

------

原因：

简单可靠。

------

未来可以升级：

```
Extension

+

MIME Type

+

Content Detection
```

------

# 10. File Type Mapping

需要统一转换：

文件后缀：

```
.pdf
.docx
.md
.txt
```

转换为：

```
DocumentType
```

例如：

```
.pdf

    |

    v

DocumentType.PDF
```

------

# 11. Dispatcher Implementation

核心逻辑：

```
class DocumentDispatcher:


    def dispatch(
        self,
        file_path:str
    )->Document:


        file_type = detect_file_type(
            file_path
        )


        parser_class = registry.get(
            file_type
        )


        parser = parser_class()


        return parser.parse(
            file_path
        )
```

------

# 12. Metadata Handling

## Decision

Dispatcher 不修改 Parser 生成的 Metadata。

原因：

Parser 输出：

```
Document
```

已经满足 Model。

------

但是：

未来如果需要补充：

```
source

tenant

permission

owner
```

推荐位置：

```
Document Service Layer
```

而不是 Dispatcher。

------

# 13. Error Handling

新增：

```
dispatcher/exceptions.py
```

------

## UnsupportedFileTypeError

场景：

上传：

```
xxx.exe
```

但是没有 Parser。

抛出：

```
UnsupportedFileTypeError
```

------

## ParserNotFoundError

场景：

文件类型存在：

```
xlsx
```

但是 Registry 没有注册。

------

# 14. Complete Workflow

最终流程：

```
file_path


   |

   v


Dispatcher


   |

   +----------------+

   |                |

 pdf              docx

   |                |

PDFParser       DocxParser


   |

   v


Document
```

------

# 15. Implementation Order

Coding Agent 实现顺序：

## Step 1

创建：

```
document/dispatcher/exceptions.py
```

实现：

```
UnsupportedFileTypeError

ParserNotFoundError
```

------

## Step 2

创建：

```
document/dispatcher/registry.py
```

实现：

```
PARSER_REGISTRY
```

------

## Step 3

创建：

```
document/dispatcher/dispatcher.py
```

实现：

```
DocumentDispatcher
```

------

## Step 4

创建：

```
document/dispatcher/__init__.py
```

统一导出。

------

# 16. Acceptance Criteria

完成后必须满足：

## 1. PDF 自动选择 PDFParser

输入：

```
test.pdf
```

执行：

```
dispatcher.dispatch(
    "test.pdf"
)
```

返回：

```
Document
```

------

## 2. Markdown 自动选择 MarkdownParser

输入：

```
README.md
```

返回：

```
Document
```

------

## 3. 不支持格式抛异常

例如：

```
test.exe
```

返回：

```
UnsupportedFileTypeError
```

------

## 4. Dispatcher 不包含解析逻辑

禁止：

```
extract_pdf_text()

read_docx()

clean()
```

------

# 17. Final Architecture

最终 Document 模块：

```
document


├── model

│
│   Document

│
│
├── parser

│
│   BaseParser

│   PDFParser

│   MarkdownParser

│   DocxParser

│
│
└── dispatcher

    Parser Registry

    Parser Selection
```

------

# Summary

Dispatcher 的核心职责：

```
选择谁处理

而不是

自己处理
```

架构原则：

```
Model
负责数据

Parser
负责转换

Dispatcher
负责调度
```

保持：

```
High Cohesion

Low Coupling
```