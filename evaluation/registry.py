"""evaluation.registry — 评测模块注册初始化。"""

from core.logger import get_logger
from core.registry import get_registry
from evaluation.metric import (
    RecallMetric,
    PrecisionMetric,
    MRRMetric,
    NDCGMetric,
    HitRateMetric,
    DiversityScore,
    CoverageScore,
)
from evaluation.analyzer import RetrievalTraceAnalyzer
from evaluation.debug import RetrievalDebugger

logger = get_logger("evaluation.registry")


def register_evaluation_module() -> None:
    """注册 Evaluation 模块组件到全局 RegistryCenter。"""
    rc = get_registry()

    # 注册 Metric 类
    rc.model.register("RecallMetric", RecallMetric)
    rc.model.register("PrecisionMetric", PrecisionMetric)
    rc.model.register("MRRMetric", MRRMetric)
    rc.model.register("NDCGMetric", NDCGMetric)
    rc.model.register("HitRateMetric", HitRateMetric)
    rc.model.register("DiversityScore", DiversityScore)
    rc.model.register("CoverageScore", CoverageScore)
    logger.info("Evaluation Metrics 注册完成")

    # 注册 Analyzer
    analyzer = RetrievalTraceAnalyzer()
    rc.service.register("trace_analyzer", analyzer)
    logger.info("Trace Analyzer 注册完成")

    # 注册 Debugger
    debugger = RetrievalDebugger()
    rc.service.register("retrieval_debugger", debugger)
    logger.info("Retrieval Debugger 注册完成")
