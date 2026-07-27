"""Generation 域数据模型。"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    """生成请求。

    Attributes:
        query:         用户问题。
        context:       检索返回的上下文字符串（ContextBuilder 产出）。
        system_prompt: 自定义 system prompt，为 None 时使用默认。
        model:         模型名，为 None 时使用配置默认值。
    """
    query: str
    context: str = ""
    system_prompt: Optional[str] = None
    model: Optional[str] = None


class GenerationResponse(BaseModel):
    """生成响应。

    Attributes:
        answer:  LLM 生成的答案。
        model:   使用的模型名。
        sources: 引用的来源列表（V2 增强）。
    """
    answer: str
    model: str = ""
    sources: List[Dict[str, Any]] = Field(default_factory=list)
