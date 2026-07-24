ADR-006-developer-validation-center-design.md

这个 ADR 定义的是 前端 Developer Validation Center，不是后端 Validation 模块。

两者关系：

Developer Validation Center
        |
        | HTTP API
        v
Validation Module
        |
        v
业务模块
(Ingress / Document / Processor / Retriever)
# ADR-006 Developer Validation Center Design

## Status

Proposed


## Module

BestRAG Developer Validation Center


## Version

v1.0


---

# 1. Overview


## 1.1 Background


目前 BestRAG 已完成：

- Ingress Module
- Document Module
- Validation Module


当前系统已经具备：


File Upload

|

v

Document Pipeline

|

v

Validation API



但是目前验证方式主要依赖：

- Swagger UI
- API 调试工具
- 手动调用接口


存在问题：

1. 不直观
2. 无法快速查看验证结果
3. 不方便开发阶段持续调试


因此设计 Developer Validation Center。


---

# 2. Design Goal


Developer Validation Center 的目标：


## 2.1 提供统一验证入口


开发人员通过 Web 页面：


Upload

|

Validation

|

Result



完成模块验证。


---

## 2.2 不包含业务逻辑


Frontend 只负责：

- 调用 Validation API
- 展示结果
- 展示日志


禁止：

- 文件解析
- Document 创建
- Processor 调用


---

# 3. Architecture


整体结构：


Frontend

Developer Validation Center

    |

    | HTTP

    v

FastAPI

    |

    v

Validation API

    |

    v

ValidationService

    |

    v

Business Modules



---

# 4. Frontend Position


Developer Validation Center 属于：


Developer Tool Layer



不是：


Business User Interface



区别：

业务 UI：


用户上传知识库文件


Developer UI：


验证系统内部模块



---

# 5. Page Design


第一阶段包含三个区域：



Developer Validation Center

+-----------------------+

| Upload Information |

+-----------------------+

| Validation Actions |

+-----------------------+

| Validation Result |

+-----------------------+



---

# 6. Upload Information


## Responsibility


展示最近上传文件。


数据来源：

Ingress API


显示：

```json
{
 filename:"test.pdf",

 size:"2MB",

 upload_time:"xxx",

 path:"workspace/files/test.pdf"
}
7. Validation Actions
Document Validation

按钮：

Validate Document

调用：

POST

/validation/document

请求：

{
 "file_path":"workspace/test.pdf"
}
Full Regression

按钮：

Run Document Regression

调用：

POST

/validation/document/all

执行：

TXT

Markdown

PDF

DOCX

Exception Cases
8. Validation Result

展示：

ValidationReport

例如：

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
9. Frontend Component Design

建议目录：

static/


├── index.html


├── validation/


│
├── validation.html


├── validation.js


└── validation.css

10. Frontend Flow
Step 1

用户上传文件

Frontend

 |

 v

Ingress API

 |

 v

Workspace
Step 2

获取文件信息

Frontend 保存：

file_path
Step 3

点击验证

调用：

/validation/document
Step 4

展示结果

例如：

✅ Document Validation Success


Parser:

PDFParser


Content:

12000 chars


Metadata:

filename=test.pdf
11. Backend Integration

main.py 只需要：

app.mount(
    "/validation",
    StaticFiles(...)
)

或者：

注册前端页面 Router。

禁止：

main.py

    |
    + validation logic
12. Dependency

Frontend:

Developer Center

        |

        v

Validation API

Backend:

Validation API

        |

        v

ValidationService

        |

        v

DocumentService

13. Future Extension

Developer Validation Center 设计必须支持扩展。

未来增加：

Processor Validation

新增按钮：

Validate Processor

调用：

POST

/validation/processor

展示：

Chunk Count

Average Length

Metadata
Retriever Validation

新增：

Validate Retriever

展示：

Embedding Status

Vector Store Status

Search Result
14. Error Display

统一展示：

成功：

GREEN

Validation Success

失败：

RED

Validation Failed

Error Message

例如：

UnsupportedFileTypeError

File extension .exe not supported
15. Security Consideration

当前：

Developer Mode

允许：

localhost

未来生产环境：

需要：

Authentication
Permission Control
Disable Validation API
16. Implementation Order
Step 1

创建前端页面：

static/validation/
Step 2

实现：

validation.html

包含：

文件信息
验证按钮
结果区域
Step 3

实现：

validation.js

负责：

API 调用
JSON 解析
页面更新
Step 4

集成 FastAPI

main.py:

只注册静态资源。

Step 5

测试：

流程：

Upload File


    ↓


Open Validation Center


    ↓


Validate Document


    ↓


Show Report

17. Acceptance Criteria

完成后必须满足：

1

开发者无需 Swagger：

可以通过页面完成：

Document Validation
2

验证结果可视化：

包含：

status
parser
document_id
metadata
error
3

Frontend 无业务逻辑

4

未来增加模块验证：

只增加：

API
页面组件

无需修改整体架构。

Final Architecture

最终：

                 Developer

                     |

                     v

       Developer Validation Center


                     |

                     v


              Validation API


                     |

                     v


        +------------+-------------+

        |                          |

   Document Validation      Processor Validation


        |

        v


    BestRAG Modules

Summary

Developer Validation Center 定位：

系统开发控制台

不是业务页面

核心原则：

Frontend负责展示

Validation负责验证

业务模块负责执行

END


---

实现完成后，你当前架构会形成一个非常清晰的开发闭环：

```text
开发新模块
    |
实现模块
    |
增加 Validation
    |
增加 Developer Center 按钮
    |
可视化验证