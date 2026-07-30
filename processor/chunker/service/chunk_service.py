"""ChunkService — Chunk 编排层 + Strategy Registry。

调用方只传策略名，ChunkService 负责查找 Strategy 并执行切分。

v0.2 升级：
- 本地 CHUNK_STRATEGIES 保持向后兼容
- 新策略通过 RegistryCenter 注册
- ChunkService 优先使用 RegistryCenter 中的策略
"""

from typing import Optional

from document.model import Document

from core.logger import get_logger
from core.registry import get_registry
from core.strategy import StrategyFactory
from processor.chunker.model import Chunk
from processor.chunker.strategy import (
    BaseChunkStrategy,
    FixedChunkStrategy,
    HeadingChunkStrategy,
    HierarchicalChunkStrategy,
    RecursiveChunkStrategy,
    SemanticChunkStrategy,
)

logger = get_logger("bestrag.chunk_service")

# Strategy Registry — 策略名字符串 → 策略实例（v0.1 兼容）
CHUNK_STRATEGIES: dict[str, BaseChunkStrategy] = {
    "fixed": FixedChunkStrategy(),
    "recursive": RecursiveChunkStrategy(),
    "heading": HeadingChunkStrategy(),
    "semantic": SemanticChunkStrategy(),
    "hierarchical": HierarchicalChunkStrategy(),
}


class ChunkService:
    """Chunk 编排服务。

    Usage::

        service = ChunkService()
        chunks = service.chunk(document, strategy="recursive")
    """

    def __init__(self):
        self._factory = StrategyFactory()
        self._registry_inited = False

    def _ensure_registry(self) -> None:
        """确保已有策略已注册到 RegistryCenter（只执行一次）。"""
        if self._registry_inited:
            return
        registry = get_registry()
        for name, instance in CHUNK_STRATEGIES.items():
            key = f"chunk:{name}"
            if not registry.strategy.has(key):
                registry.strategy.register(key, instance.__class__)
                logger.info(f"注册 Chunk 策略: {key}")
        self._registry_inited = True

    def chunk(self, document: Document, strategy: str = "recursive") -> list[Chunk]:
        """将 Document 按指定策略切分为 Chunk 列表。

        优先使用 RegistryCenter 中的策略，兼容 v0.1 本地策略字典。

        Args:
            document: Document 对象（通常来自 Cleaner 的输出）。
            strategy: 策略名（如 "fixed" / "recursive"）。

        Returns:
            Chunk 列表，每个 Chunk 的 document_id 指向来源 Document.id。

        Raises:
            ValueError: strategy 不可用。
        """
        # 1. 尝试新框架（RegistryCenter）
        instance = self._get_from_registry(strategy)
        if instance is not None:
            return instance.split(document.content, document.id)

        # 2. 回退到 v0.1 本地策略字典
        instance = CHUNK_STRATEGIES.get(strategy)
        if instance is not None:
            return instance.split(document.content, document.id)

        # 3. 策略不可用
        available = ", ".join(self._list_available())
        raise ValueError(f"未知策略: '{strategy}'，可用策略: [{available}]")

    def _get_from_registry(self, name: str) -> Optional[BaseChunkStrategy]:
        """从 RegistryCenter 获取策略实例。"""
        self._ensure_registry()
        registry = get_registry()
        key = f"chunk:{name}"
        if registry.strategy.has(key):
            try:
                strategy_cls = registry.strategy.get(key)
                # 尝试携带参数创建实例
                return strategy_cls()
            except Exception as e:
                logger.warning(f"策略 '{key}' 实例化失败: {e}")
                return None
        return None

    def _list_available(self) -> list[str]:
        """列出所有可用策略名。"""
        names = list(CHUNK_STRATEGIES.keys())
        return names
