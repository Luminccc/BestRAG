"""PromptBuilder — 将 context + query + system prompt 组装为 LLM messages。

系统 prompt 来源优先级：调用参数 > 配置文件 > 内置默认值。
"""

from typing import Any, Dict, List, Optional

from core.config import get_config

# 内置默认 system prompt
_DEFAULT_SYSTEM_PROMPT = "你是企业知识助手，基于以下文档回答问题。如果文档中没有相关信息，请如实说明。"


class PromptBuilder:
    """System Prompt + Context + Query → OpenAI messages。"""

    def build(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """构建 messages 列表。

        Args:
            query:         用户原始问题。
            context:       ContextBuilder 产出的上下文字符串。
            system_prompt: 自定义 system prompt，为 None 时使用默认值。

        Returns:
            格式：
            [
                {"role": "system", "content": "<system_prompt>"},
                {"role": "user", "content": "问题 + 上下文"},
            ]
        """
        # system prompt 优先级：参数 > config > 默认
        if system_prompt is None:
            system_prompt = self._default_system_prompt()

        user_content = self._build_user_content(query, context)

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

    def _build_user_content(self, query: str, context: str) -> str:
        if context:
            return f"问题：{query}\n\n参考文档：\n{context}"
        return f"问题：{query}"

    def _default_system_prompt(self) -> str:
        """从配置读取默认 system prompt，无配置则用内置值。"""
        try:
            cfg = get_config().generation
            if cfg.system_prompt:
                return cfg.system_prompt
        except Exception:
            pass
        return _DEFAULT_SYSTEM_PROMPT
