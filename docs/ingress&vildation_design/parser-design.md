ADR-006-document-parser-design.md

这个文档只针对：

document/parser

模块设计。

定位是给 coding agent 直接实现使用。

# ADR-006 Document Parser Design

## Status

Proposed


## Module

BestRAG Document Parser Module


## Version

v1.0


---

# 1. Overview


## 1.1 Module Position


`document/parser` 是 Document 模块中的文档解析层。


它负责：

> 将不同格式的文件转换为统一的 Document Model。


整体流程：



Input File

|

v

Document Parser

|

v

Document Model

|

v

Processor

|

v

Chunk



---

# 2. Responsibility


## 2.1 Parser Does


Parser 负责：


- 文件内容读取
- 文件格式解析
- 内容提取
- 生成 Document 对象


即：



File Format

  |

  v

Document Object



---

## 2.2 Parser Does Not Do


Parser 不负责：


## 文档清洗


属于：


processor/cleaner



---

## 文档切片


属于：


processor/chunker



---

## Metadata 增强


属于：


processor/transformer



---

## Embedding


属于：


retriever/embedding



---

## Vector Storage


属于：


retriever/vector_store



---

# 3. Design Principle


## 3.1 Single Responsibility


Parser 只负责：


格式转换



禁止：

```python
class PDFParser:

    def clean():
        pass

    def chunk():
        pass

    def embed():
        pass
3.2 Unified Output

所有 Parser 必须输出：

Document

例如：

PDFParser

      |

      v

Document



MarkdownParser

      |

      v

Document

上层不关心文件格式。

3.3 Open Extension

新增格式时：

例如：

ExcelParser

HTMLParser

PPTParser

只需要新增 Parser。

不修改：

Processor
Retriever
Dispatcher
4. Technology Selection
4.1 Parser Language

Python

版本：

Python 3.12+
4.2 Parser Framework

不使用大型框架。

采用：

Native Parser Adapter Pattern

原因：

结构简单
容易扩展
避免框架绑定
5. Directory Structure

推荐：

document

└── parser

    ├── base.py

    ├── pdf_parser.py

    ├── markdown_parser.py

    ├── docx_parser.py

    └── txt_parser.py
6. BaseParser Design
6.1 Responsibility

定义所有 Parser 的统一接口。

6.2 Interface
from abc import ABC, abstractmethod


class BaseParser(ABC):


    @abstractmethod

    def parse(
        self,
        file_path: str
    ) -> Document:

        pass
7. Parser Input Design
Decision

Parser 输入：

file_path: str

原因：

Parser 属于 Document 模块。

不应该依赖：

Ingress

避免：

document

    |

    强依赖

    |

ingress

未来如果需要更多信息：

可以扩展：

ParserInput

例如：

class ParserInput:

    file_path:str

    filename:str

    source:str

但 MVP 阶段不需要。

8. PDF Parser Design
8.1 Technology Selection

推荐：

PyMuPDF

原因：

性能高
支持 PDF 文本提取
API 简单
社区成熟
8.2 Dependency
pymupdf

安装：

pip install pymupdf
8.3 Processing Flow
PDF File

    |

    v

PyMuPDF

    |

    v

Extract Text

    |

    v

Document
8.4 Implementation

示例：

class PDFParser(BaseParser):


    def parse(
        self,
        file_path:str
    )->Document:


        text = extract_text(file_path)


        return Document(

            content=text,

            metadata=DocumentMetadata(...)

        )
9. Markdown Parser Design
Technology

推荐：

markdown

或者：

python-markdown
Flow
Markdown File

      |

      v

Read Content

      |

      v

Document
Implementation
class MarkdownParser(BaseParser):


    def parse(
        self,
        file_path:str
    )->Document:


        content=open(
            file_path
        ).read()


        return Document(
            content=content,
            metadata=...
        )
10. TXT Parser Design
Flow
TXT File

   |

   v

Read Text

   |

   v

Document

实现简单：

class TXTParser(BaseParser):

    def parse(file_path):

        text=open(
            file_path
        ).read()


        return Document(...)
11. DOCX Parser Design
Technology

推荐：

python-docx
Flow
DOCX

 |

 v

python-docx

 |

 v

Extract Paragraphs

 |

 v

Document
12. Metadata Generation

Parser 创建 Document 时需要填充基础 Metadata。

例如：

DocumentMetadata(

    filename="test.pdf",

    file_type=DocumentType.PDF,

    source="upload",

    created_time=datetime.now()

)

注意：

Parser 只生成：

基础 Metadata

不生成：

关键词

摘要

标签

这些属于：

processor/transformer
13. Error Handling

Parser 必须处理：

文件不存在

返回：

FileNotFoundError
文件格式错误

返回：

ParserError
内容为空

返回：

EmptyDocumentError

建议：

新增：

parser/exceptions.py

未来统一管理。

14. Parser Factory Compatibility

Parser 本身不负责选择。

例如：

错误：

if type=="pdf":

    PDFParser()

应该交给：

document/dispatcher

Parser 只负责解析。

15. Implementation Order

Coding Agent 实现顺序：

Step 1

创建：

document/parser/base.py

实现：

BaseParser
Step 2

实现：

txt_parser.py

原因：

最简单，验证流程。

Step 3

实现：

markdown_parser.py
Step 4

实现：

pdf_parser.py

依赖：

PyMuPDF
Step 5

实现：

docx_parser.py

依赖：

python-docx
16. Acceptance Criteria

完成后必须满足：

1

所有 Parser 返回：

Document
2

不同格式文件：

PDF

DOCX

Markdown

TXT

可以转换为：

Document
3

Parser 不包含：

clean()

chunk()

embed()
4

Processor 可以直接消费：

Document
17. Final Architecture

最终结构：

document


├── model

│
│   Document

│
│
├── parser

│

│   BaseParser

│

│   PDFParser

│

│   MarkdownParser

│

│   DocxParser

│

│
└── dispatcher

        Parser Selection
Summary

Document Parser 的核心目标：

Any File

    |

    v

Document Object

设计原则：

Parser负责转换

Model负责定义

Dispatcher负责选择

保持：

High Cohesion

Low Coupling