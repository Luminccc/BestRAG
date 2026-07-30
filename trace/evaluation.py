"""EvaluationTrace — 评测 Trace 接口（v0.3 Phase 2 预留）。

连接 Phase 4 Evaluation Framework。
"""

from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.models.trace import Metric, Span, SpanStatus, Trace, TraceStatus, TraceType
from trace.context import TraceContext

logger = get_logger("trace.evaluation")


class EvaluationTrace:
    """评测 Trace 助手。

    用于记录评测执行过程的 Trace 数据。
    Phase 3 Evaluation Framework 将基于此构建。
    """

    @staticmethod
    def record(
        ctx: TraceContext,
        dataset_name: str,
        strategy_name: str,
        metrics: Dict[str, float],
        status: str = "success",
    ) -> None:
        """记录一次评测执行。

        Args:
            ctx: TraceContext 实例。
            dataset_name: 评测数据集名称。
            strategy_name: 评测策略名称。
            metrics: 指标字典 {"recall@5": 0.92, ...}。
            status: 评测状态。
        """
        trace = ctx.start_trace(
            TraceType.EVALUATION,
            metadata={
                "dataset": dataset_name,
                "strategy": strategy_name,
            },
        )

        for name, value in metrics.items():
            ctx.record_metric(name, value, tags={"dataset": dataset_name})

        ctx.end_trace(TraceStatus.SUCCESS if status == "success" else TraceStatus.FAILED)
        logger.info(
            f"评测 Trace 已记录: dataset={dataset_name}, "
            f"strategy={strategy_name}, metrics={len(metrics)}"
        )
