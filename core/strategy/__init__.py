"""Core Strategy — 统一策略框架。

提供：
- BaseStrategy    : 所有策略的抽象基类
- BaseChunkStrategy    : Chunk 切分策略接口
- BaseRetrievalStrategy: 检索策略接口
- BaseFusionStrategy   : 融合策略接口
- StrategyPipeline     : 策略流水线
- StrategyFactory      : 策略工厂

用法::

    from core.strategy import BaseChunkStrategy, StrategyPipeline, StrategyFactory
"""

from core.strategy.base import BaseStrategy
from core.strategy.chunk import BaseChunkStrategy
from core.strategy.retrieval import BaseRetrievalStrategy
from core.strategy.fusion import BaseFusionStrategy
from core.strategy.pipeline import StrategyPipeline
from core.strategy.factory import StrategyFactory

__all__ = [
    "BaseStrategy",
    "BaseChunkStrategy",
    "BaseRetrievalStrategy",
    "BaseFusionStrategy",
    "StrategyPipeline",
    "StrategyFactory",
]
