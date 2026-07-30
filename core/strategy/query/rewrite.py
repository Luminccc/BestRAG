"""BaseQueryRewriteStrategy — 查询重写策略基类。

将用户原始查询重写为更适合检索的表达形式。
"""

from abc import abstractmethod
from typing import Any

from core.strategy.base import BaseStrategy


class BaseQueryRewriteStrategy(BaseStrategy):
    """查询重写策略基类。"""

    name: str = "base_rewrite"

    @abstractmethod
    def rewrite(self, query: str, **kwargs: Any) -> str:
        """重写查询。

        Args:
            query: 用户原始查询。
            **kwargs: 扩展参数（上下文、历史等）。

        Returns:
            重写后的查询。
        """

    def execute(self, query: str, **kwargs: Any) -> str:
        return self.rewrite(query, **kwargs)


class SimpleQueryRewriteStrategy(BaseQueryRewriteStrategy):
    """简单查询重写 — 规则方式（补全、同义替换）。"""

    name: str = "simple_rewrite"

    def __init__(self):
        # 常见缩写/简称替换规则
        self._replacements = {
            "milvus": "Milvus 向量数据库",
            "bge": "BGE Embedding 模型",
            "llm": "大语言模型",
            "rag": "RAG 检索增强生成",
        }

    def rewrite(self, query: str, **kwargs: Any) -> str:
        result = query
        for short, full in self._replacements.items():
            if short in result.lower():
                result = result.replace(short, full)
        return result if result != query else query


class LLMQueryRewriteStrategy(BaseQueryRewriteStrategy):
    """LLM 查询重写 — 使用 LLMProvider 重写查询。"""

    name: str = "llm_rewrite"

    def __init__(self, llm_provider=None):
        self._llm = llm_provider

    def rewrite(self, query: str, **kwargs: Any) -> str:
        if self._llm is None:
            return query
        messages = [
            {"role": "system", "content": "将用户的查询重写为更详细、适合知识库检索的形式。"},
            {"role": "user", "content": f"查询：{query}"},
        ]
        try:
            return self._llm.generate(messages, temperature=0.1)
        except Exception:
            return query
