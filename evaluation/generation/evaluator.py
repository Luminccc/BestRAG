"""Generation Evaluation — 生成质量评测（预留）。"""

from typing import Any, List

from evaluation.core.evaluator import BaseEvaluator
from evaluation.core.metric import MetricResult


class AnswerEvaluator(BaseEvaluator):
    """生成答案评测器（预留 — 未来支持 RAGAS / LLM Judge）。"""

    name: str = "answer_evaluator"

    def evaluate(self, answer: str = "", context: str = "", **kwargs: Any) -> List[MetricResult]:
        # v0.2 返回占位指标
        return [MetricResult(name="answer_length", value=float(len(answer)))]
