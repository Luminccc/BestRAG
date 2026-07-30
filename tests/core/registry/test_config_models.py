"""Config Models 单元测试。"""

from core.config import CoreConfig
from core.config_models.strategy import ChunkStrategyConfig, StrategyConfig
from core.config_models.retrieval import (
    FusionConfig,
    QueryRewriteConfig,
    RetrieverPipelineConfig,
    RetrievalPipelineConfig,
)
from core.config_models.evaluation import EvaluationConfig


class TestStrategyConfig:
    """策略配置模型测试。"""

    def test_default_values(self):
        """策略配置默认值正确。"""
        cfg = StrategyConfig()
        assert cfg.enabled is True
        assert cfg.chunk.type == "recursive"
        assert cfg.chunk.params == {}

    def test_custom_chunk(self):
        """自定义 Chunk 策略。"""
        cfg = StrategyConfig()
        cfg.chunk.type = "semantic"
        cfg.chunk.params = {"threshold": 0.8}
        assert cfg.chunk.type == "semantic"
        assert cfg.chunk.params["threshold"] == 0.8


class TestRetrievalPipelineConfig:
    """检索流水线配置模型测试。"""

    def test_default_values(self):
        """检索流水线默认值正确。"""
        cfg = RetrievalPipelineConfig()
        assert cfg.query.enabled is False
        assert cfg.query.strategy == "llm"
        assert cfg.pipeline.retrievers == ["vector", "bm25"]
        assert cfg.pipeline.fusion.type == "rrf"
        assert cfg.pipeline.top_k == 10

    def test_custom_pipeline(self):
        """自定义检索流水线。"""
        cfg = RetrievalPipelineConfig()
        cfg.query.enabled = True
        cfg.pipeline.retrievers = ["vector", "bm25", "context"]
        cfg.pipeline.fusion.type = "weighted"
        cfg.pipeline.fusion.weights = [0.6, 0.4]
        assert cfg.pipeline.retrievers == ["vector", "bm25", "context"]
        assert cfg.pipeline.fusion.type == "weighted"
        assert cfg.pipeline.fusion.weights == [0.6, 0.4]


class TestEvaluationConfig:
    """Evaluation 配置测试。"""

    def test_default_values(self):
        """Evaluation 默认值正确。"""
        cfg = EvaluationConfig()
        assert cfg.enabled is False
        assert "recall" in cfg.metrics
        assert "mrr" in cfg.metrics


class TestCoreConfigExtension:
    """CoreConfig v0.2 扩展字段测试。"""

    def test_core_config_has_new_sections(self):
        """CoreConfig 包含 v0.2 新增配置段。"""
        cfg = CoreConfig()
        assert hasattr(cfg, "strategy")
        assert hasattr(cfg, "retrieval_pipeline")
        assert hasattr(cfg, "evaluation")

    def test_strategy_section_defaults(self):
        """strategy 配置段默认值与 StrategyConfig 一致。"""
        cfg = CoreConfig()
        assert cfg.strategy.chunk.type == "recursive"
        assert cfg.strategy.enabled is True

    def test_retrieval_pipeline_section_defaults(self):
        """retrieval_pipeline 配置段默认值与 RetrievalPipelineConfig 一致。"""
        cfg = CoreConfig()
        assert cfg.retrieval_pipeline.pipeline.fusion.type == "rrf"

    def test_evaluation_section_defaults(self):
        """evaluation 配置段默认值与 EvaluationConfig 一致。"""
        cfg = CoreConfig()
        assert cfg.evaluation.enabled is False
