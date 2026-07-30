"""StrategyPipeline — 策略流水线。

将多个 Strategy 串联执行，前一个策略的输出作为后一个策略的输入。

用法::

    pipe = StrategyPipeline([
        retriever_a,
        retriever_b,
        fusion_strategy,
    ])
    final_result = pipe.execute(query)
"""

from typing import Any, List

from core.logger import get_logger
from core.strategy.base import BaseStrategy

logger = get_logger("bestrag.strategy.pipeline")


class StrategyPipeline:
    """策略执行流水线。

    按顺序执行 strategies，每个策略的 execute 输出传递给下一个策略的 execute 输入。

    属性:
        strategies: 按执行顺序排列的策略列表。
    """

    def __init__(self, strategies: List[BaseStrategy]):
        if not strategies:
            raise ValueError("Pipeline 必须包含至少一个策略")
        self.strategies = strategies

    def execute(self, input_data: Any) -> Any:
        """依次执行所有策略。

        Args:
            input_data: 传递给第一个策略的输入。

        Returns:
            最后一个策略的输出。
        """
        result = input_data
        for i, strategy in enumerate(self.strategies):
            name = strategy.name or strategy.__class__.__name__
            logger.info(f"Pipeline Step {i + 1}: {name}")
            try:
                strategy.initialize()
                result = strategy.execute(result)
            except Exception as e:
                logger.error(f"Pipeline Step {i + 1} ({name}) 失败: {e}")
                raise
            finally:
                strategy.close()
        return result

    def __len__(self) -> int:
        return len(self.strategies)

    def __repr__(self) -> str:
        names = [s.name or s.__class__.__name__ for s in self.strategies]
        return f"StrategyPipeline({ ' → '.join(names) })"
