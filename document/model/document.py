"""Document — 系统内部统一文档对象。

所有 Parser 的输出都必须统一为 Document 对象，
Processor 只认 Document，不认原始文件格式。

Document 是上下游模块之间的稳定契约，禁止添加业务逻辑方法。
"""

from uuid import uuid4

from pydantic import BaseModel, Field

from .metadata import DocumentMetadata


class Document(BaseModel):
    """统一文档主体。

    Attributes:
        id:       文档唯一标识，由 uuid4() 生成，用于跨模块关联
        content:  解析后的原始文本内容（非切片后的 chunk）
        metadata: 文档属性信息
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    metadata: DocumentMetadata
