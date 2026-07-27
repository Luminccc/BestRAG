"""Generation 域异常。"""

from core.exception import CoreRuntimeError


class GenerationError(CoreRuntimeError):
    """Generation 域基础异常。"""
    pass


class ProviderError(GenerationError):
    """LLM Provider 调用失败。"""
    pass


class PromptError(GenerationError):
    """Prompt 构建错误。"""
    pass


class ContextError(GenerationError):
    """上下文构建错误。"""
    pass
