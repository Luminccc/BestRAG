ADR-009-processor-cleaner-design.md

该 ADR 同时定义：

Processor 模块 Cleaner 子模块设计
Document → Clean Document 数据流
Validation 对 Cleaner 的验证扩展
Developer Validation Center 增加 Cleaner 验证入口

可以直接交给 coding agent 实现。

# ADR-009 Processor Cleaner Design

## Status

Proposed


## Module

Processor - Cleaner


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

Validation



目前 Document 输出的是原始文档内容：



Document

{

id,

content,

metadata

}



但是原始内容通常存在：

- 多余空格
- 多余换行
- 不规范字符
- 文档解析残留
- HTML/XML控制字符


这些问题会直接影响：

- Chunk质量
- Embedding效果
- Retrieval准确率


因此增加 Processor 模块。


---

# 2. Processor Architecture


Processor 总体负责：


Document

|

v

Processor

|

+-------------+

|             |

Cleaner Chunker

              |

              v

          Transformer


职责划分：

|模块|职责|
|-|-|
|Cleaner|文本规范化|
|Chunker|文本切分|
|Transformer|内容增强|


---

# 3. Cleaner Responsibility


Cleaner 只负责：


Document

|

v

Clean Document



核心目标：

提高文本质量。


---

# 4. Cleaner Responsibilities


## 4.1 Whitespace Normalize


处理：


"hello world"



转换：


"hello world"



---

## 4.2 Line Break Normalize


输入：


hello

world



输出：


hello

world



---

## 4.3 Remove Control Characters


清理：

- \x00
- 非打印字符


例如：


hello\x00world



转换：


helloworld



---

## 4.4 Trim


去除：


Document.content

前后空白



---

# 5. Cleaner Forbidden Responsibility


Cleaner 禁止：


## 5.1 Chunk


禁止：

```python
split()
chunk()

原因：

Chunker负责。

5.2 Metadata Enhancement

禁止：

summary

keywords

tags

原因：

Transformer负责。

5.3 Embedding

禁止：

embedding()

原因：

Embedding模块负责。

6. Data Model Design
6.1 Input

Cleaner输入：

Document

来自：

document.service.DocumentService
6.2 Output

第一阶段保持：

Document

即：

Cleaner:

Document

    |

    v

Document

原因：

避免新增模型复杂度。

7. Metadata Update

Cleaner允许增加处理信息。

例如：

metadata.extra

增加：

{
 "cleaned": true,

 "original_length":10000,

 "cleaned_length":8500
}

注意：

不修改原始业务字段。

8. Directory Design

新增：

processor/


├── cleaner/

│
├── service/

│
├── model/

└── __init__.py


详细：

processor/

├── cleaner/

│   ├── base.py

│   ├── text_cleaner.py

│   └── __init__.py


├── model/

│   └── process_result.py


├── service/

│   └── processor_service.py


└── __init__.py

9. Interface Design
9.1 BaseCleaner

文件：

processor/cleaner/base.py

定义：

class BaseCleaner:

    def clean(
        self,
        document: Document
    ) -> Document:

        pass
10. TextCleaner

文件：

text_cleaner.py

实现：

class TextCleaner(BaseCleaner):

    def clean(
        self,
        document: Document
    ) -> Document:

        ...

处理：

whitespace
newline
control chars
11. ProcessorService

职责：

编排 Processor 流程。

第一阶段：

ProcessorService


        |

        v


TextCleaner


        |

        v


Clean Document

接口：

process(
    document:Document
)->Document
12. Validation Extension

当前：

Validation

    |

    Document Validation

扩展：

Validation

    |

    +----------------+

    |

 Document Validation


 Cleaner Validation

13. Cleaner Validation

新增：

validation/checks/processor_check.py

负责：

Cleaner结果检查。

14. Validation API

新增：

POST

/validation/processor/cleaner

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

Cleaner


    |

    v

ValidationReport

15. Cleaner Validation Rules
15.1 Document Exists

检查：

document != None
15.2 Content Exists

检查：

len(content)>0
15.3 Cleaning Executed

检查：

metadata:

{
"cleaned":true
}
15.4 Length Comparison

记录：

{
original_length:10000,

cleaned_length:8500
}
16. Developer Validation Center

新增区域：

Processor Validation

页面：

Developer Validation Center


+----------------------+

Document

+----------------------+

Processor

   |

   [Validate Cleaner]


+----------------------+

Result

17. Implementation Order
Step 1

创建：

processor/
Step 2

实现：

BaseCleaner
Step 3

实现：

TextCleaner
Step 4

实现：

ProcessorService
Step 5

扩展：

ValidationService
Step 6

增加 API：

/validation/processor/cleaner
Step 7

增加：

Developer Validation Center

Cleaner Button
18. Acceptance Criteria

完成后：

Cleaner

支持：

空白清理
换行规范化
控制字符清理
Architecture

满足：

Document

    |

    v

Cleaner

    |

    v

Document
Validation

支持：

POST /validation/processor/cleaner

返回：

{
status:"success",

module:"cleaner",

details:{
 original_length:10000,

 cleaned_length:8500
}
}
19. Future Extension

后续：

Chunker

新增：

processor/chunker

输入：

Clean Document

输出：

Chunk[]
Transformer

新增：

processor/transformer

负责：

keywords

summary

tags

metadata enhancement
Final Architecture

最终：

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

Cleaner定位：

文本质量处理层

原则：

Cleaner负责清洗

Chunker负责切分

Transformer负责增强


END


---

补充一个架构建议：

这里我刻意没有引入 `CleanDocument` 新模型，而是保持：


Document → Document


原因是目前项目处于 MVP 阶段。

等未来 Processor 复杂度增加（例如 OCR、表格解析、多模态文档），再引入：


RawDocument

    ↓

ProcessedDocument

    ↓

Chunk


会更加合理。现在先保持简单，降低后续维护成本。