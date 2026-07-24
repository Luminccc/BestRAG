```
ADR-005-document-model-design.md
```

------

```
# ADR-005 Document Model Design

## Module

BestRAG Document Model

## Version

v1.0


---

# 1. Overview


## 1.1 Module Position


`document/model` 是 BestRAG Document 模块的数据模型层。


它负责定义：

> 文档在系统内部流转时的统一数据结构。


整个 Document 流程：
```

Original File

```
  |

  v
```

Parser

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
  |

  v
```

Chunk

```
  |

  v
```

Embedding

```
  |

  v
```

Vector Store

```
其中：

- Parser 负责生成 Document
- Model 负责定义 Document
- Processor 负责进一步处理 Document


---

# 2. Responsibility


## 2.1 What Model Does


Model 负责：

- 定义 Document 数据结构
- 定义 Metadata 数据结构
- 提供数据校验
- 提供序列化能力


简单理解：
```

Model = Document 数据协议

```
---

## 2.2 What Model Does Not Do


Model 不负责：


### 文档解析

例如：

PDF读取

属于：
```

document/parser

```
---

### 文档清洗


属于：
```

processor/cleaner

```
---

### 文档切片


属于：
```

processor/chunker

```
---

### Embedding


属于：
```

retriever/embedding

```
---

### Vector Storage


属于：
```

retriever/vector_store

```
---

# 3. Design Principle


## 3.1 Single Responsibility


Model 只负责数据。


禁止：

​```python
class Document:

    def clean():
        pass

    def chunk():
        pass
```

原因：

Document 是数据对象，不应该包含业务逻辑。

------

## 3.2 Stable Contract

Model 是上下游模块之间的数据契约。

例如：

Parser:

```
PDF
 |
 v
Document
```

Processor:

```
Document
 |
 v
Chunk
```

所以 Document 的结构必须稳定。

------

## 3.3 Extensible

设计时考虑未来扩展。

例如未来支持：

- Page
- Table
- Image
- Section

但是 MVP 阶段保持简单。

------

# 4. Technology Selection

## 4.1 Python

项目语言：

```
Python 3.12+
```

------

## 4.2 Pydantic

推荐：

```
pydantic v2
```

原因：

### Type Validation

自动检查字段类型。

例如：

```
filename: str
```

避免错误数据进入系统。

------

### Serialization

支持：

```
Object

    |

    v

JSON
```

方便：

- API 返回
- 数据保存
- 模块通信

------

### IDE Support

提供：

- 类型提示
- 自动补全
- 静态检查

------

# 5. Directory Structure

建议：

```
document

└── model

    ├── document.py

    ├── metadata.py

    └── enums.py
```

------

# 6. Data Model Design

Document 模块包含两个核心模型：

```
Document

    +

DocumentMetadata
```

关系：

```
Document


 ├── id

 ├── content

 └── metadata

          |

          v

   DocumentMetadata
```

------

# 7. DocumentMetadata Design

## 7.1 Responsibility

保存文档基础信息。

例如：

- 文件名称
- 文件类型
- 来源
- 创建时间
- 扩展属性

------

## 7.2 Definition

```
from pydantic import BaseModel


class DocumentMetadata(BaseModel):

    filename: str

    file_type: str

    source: str | None = None

    created_time: str | None = None

    extra: dict = {}
```

------

# 7.3 Field Description

## filename

文件名称。

Example:

```
paper.pdf
```

------

## file_type

文件类型。

Example:

```
pdf

docx

markdown
```

------

## source

文档来源。

Example:

```
upload

local

url
```

------

## created_time

创建时间。

Example:

```
2026-01-01
```

------

## extra

扩展字段。

用于未来保存额外信息。

Example:

```
{
    "author":"xxx",

    "language":"zh"
}
```

------

# 8. Document Model Design

## 8.1 Responsibility

Document 是系统内部统一文档对象。

所有 Parser 必须输出：

```
Document
```

------

## 8.2 Definition

```
from pydantic import BaseModel


class Document(BaseModel):

    id: str

    content: str

    metadata: DocumentMetadata
```

------

# 8.3 Field Description

## id

文档唯一标识。

作用：

建立后续关联。

例如：

```
Document

    |

    v

Chunk

    |

    v

Embedding
```

------

## content

解析后的正文内容。

Example:

```
This is document content.
```

注意：

这里保存的是：

```
原始解析文本
```

不是：

```
chunk
```

------

## metadata

文档基础信息。

类型：

```
DocumentMetadata
```

------

# 9. Future Extension

未来可以扩展：

## Page

支持 PDF 页级结构。

Example:

```
class Page:

    page_number:int

    content:str
```

------

## Document Structure

未来：

```
Document

    |

    +-- Page

          |

          +-- Block
```

------

但是当前 MVP 不实现。

------

# 10. Implementation Steps

## Step 1

创建目录：

```
document/model
```

------

## Step 2

实现：

```
metadata.py
```

包含：

```
DocumentMetadata
```

------

## Step 3

实现：

```
document.py
```

包含：

```
Document
```

------

## Step 4

实现：

```
enums.py
```

例如：

```
from enum import Enum


class DocumentType(str, Enum):

    PDF="pdf"

    DOCX="docx"

    MARKDOWN="markdown"
```

------

# 11. Usage Example

Parser 使用：

```
document = Document(

    id="123",

    content="hello world",

    metadata=DocumentMetadata(

        filename="test.pdf",

        file_type="pdf"

    )

)
```

------

# 12. Acceptance Criteria

完成后必须满足：

## 1

Parser 可以创建 Document。

Example:

```
PDFParser

    |

    v

Document
```

------

## 2

Document 可以被 Processor 使用。

Example:

```
Document

    |

    v

Cleaner
```

------

## 3

Model 不包含任何业务逻辑。

禁止：

```
clean()

chunk()

embed()
```

------

# 13. Final Summary

Document Model 的核心思想：

```
Document Model

=

统一数据协议
```

职责：

| Component | Responsibility |
| --------- | -------------- |
| Document  | 定义文档主体   |
| Metadata  | 保存文档属性   |
| Enum      | 定义固定类型   |

最终目标：

```
Any File Format

        |

        v

Unified Document Object

        |

        v

BestRAG Pipeline
```