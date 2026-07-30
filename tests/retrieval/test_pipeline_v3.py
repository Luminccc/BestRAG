"""Retrieval Pipeline V3 集成测试。"""

from retrieval.pipeline_v3 import RetrievalPipelineV3, RetrievalTrace


class TestRetrievalTrace:
    """RetrievalTrace 测试。"""

    def test_default_trace(self):
        trace = RetrievalTrace()
        d = trace.to_dict()
        assert d["query"] == ""
        assert d["strategies"] == []


class TestRetrievalPipelineV3:
    """RetrievalPipelineV3 基础测试。"""

    def test_pipeline_initialization(self):
        pipeline = RetrievalPipelineV3()
        assert pipeline.get_retriever_names() != []

    def test_retriever_registration(self):
        pipeline = RetrievalPipelineV3()
        names = pipeline.get_retriever_names()
        assert "vector" in names
        assert "bm25" in names
        assert "hybrid" in names

    def test_build_context_empty(self):
        pipeline = RetrievalPipelineV3()
        context = pipeline.build_context([])
        assert context == ""

    def test_pipeline_repr(self):
        pipeline = RetrievalPipelineV3()
        # 验证 pipeline 能列出可用检索器
        assert len(pipeline.get_retriever_names()) >= 3
