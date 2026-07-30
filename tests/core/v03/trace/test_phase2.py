"""BestRAG v0.3 Phase 2 测试 — Trace & Observability Framework。

覆盖：
1. Model 测试     — Trace / Span / Event / Metric
2. Context 测试   — TraceContext 生命周期、Span 自动管理
3. Storage 测试   — MemoryTraceStorage CRUD
4. Collector 测试 — DefaultTraceCollector
5. Index Trace 测试 — IndexPipelineManager Trace 集成
6. Retrieval Trace  — RetrievalPipelineV3 Trace 集成
7. Generation Trace — GenerationTrace 接口
8. Evaluation Trace — EvaluationTrace 接口
9. TraceService    — Visualization API
10. 集成测试       — 完整端到端 Trace 流程

运行::

    uv run pytest tests/core/v03/trace/test_phase2.py -v
"""

import pytest
from datetime import datetime

from core.models.trace import (
    Trace, TraceType, TraceStatus,
    Span, SpanStatus,
    Event, Metric,
)
from core.models.knowledge import IndexRecord, IndexStatus
from trace import (
    TraceContext,
    TraceService,
    EvaluationTrace,
    GenerationTrace,
    DefaultTraceCollector,
    MemoryTraceStorage,
)
from trace.collector import BaseTraceCollector
from trace.storage import BaseTraceStorage
from knowledge import IndexPipelineManager


# ═══════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════

@pytest.fixture
def storage():
    return MemoryTraceStorage()


@pytest.fixture
def collector(storage):
    return DefaultTraceCollector(storage=storage)


@pytest.fixture
def ctx(collector):
    return TraceContext(collector=collector)


# ═══════════════════════════════════════════════════
# Test 1: Model 测试
# ═══════════════════════════════════════════════════

class TestTraceModel:
    def test_create_trace(self):
        t = Trace(trace_type=TraceType.RETRIEVAL)
        assert t.trace_type == TraceType.RETRIEVAL
        assert t.status == TraceStatus.PENDING
        assert t.id is not None

    def test_trace_to_dict(self):
        t = Trace(trace_type=TraceType.INDEX, status=TraceStatus.SUCCESS)
        d = t.to_dict()
        assert d["trace_type"] == "index"
        assert d["status"] == "success"

    def test_trace_types(self):
        assert TraceType.INDEX.value == "index"
        assert TraceType.RETRIEVAL.value == "retrieval"
        assert TraceType.GENERATION.value == "generation"
        assert TraceType.EVALUATION.value == "evaluation"


class TestSpanModel:
    def test_create_span(self):
        s = Span(trace_id="t1", name="embedding")
        assert s.trace_id == "t1"
        assert s.name == "embedding"
        assert s.status == SpanStatus.OK

    def test_span_duration(self):
        s = Span(trace_id="t1", name="test")
        assert s.duration_ms == 0.0

    def test_span_to_dict(self):
        s = Span(trace_id="t1", name="test", attributes={"key": "val"})
        d = s.to_dict()
        assert d["name"] == "test"
        assert d["attributes"]["key"] == "val"
        assert "duration_ms" in d

    def test_span_status_error(self):
        s = Span(trace_id="t1", name="fail", status=SpanStatus.ERROR)
        assert s.status == SpanStatus.ERROR


class TestEventModel:
    def test_create_event(self):
        e = Event(trace_id="t1", event_name="chunk_created")
        assert e.trace_id == "t1"
        assert e.event_name == "chunk_created"

    def test_event_with_payload(self):
        e = Event(trace_id="t1", event_name="error", payload={"msg": "failed"})
        assert e.payload["msg"] == "failed"


class TestMetricModel:
    def test_create_metric(self):
        m = Metric(trace_id="t1", metric_name="latency_ms", value=120.5)
        assert m.metric_name == "latency_ms"
        assert m.value == 120.5

    def test_metric_with_tags(self):
        m = Metric(trace_id="t1", metric_name="recall", value=0.92,
                   tags={"strategy": "hybrid"})
        assert m.tags["strategy"] == "hybrid"


# ═══════════════════════════════════════════════════
# Test 2: TraceContext 测试
# ═══════════════════════════════════════════════════

class TestTraceContext:
    def test_start_trace(self, ctx):
        trace = ctx.start_trace(TraceType.RETRIEVAL, request_id="req-1")
        assert trace.trace_type == TraceType.RETRIEVAL
        assert trace.request_id == "req-1"
        assert trace.start_time is not None
        assert ctx.active is True

    def test_end_trace(self, ctx, storage):
        ctx.start_trace(TraceType.RETRIEVAL)
        ctx.end_trace(TraceStatus.SUCCESS)
        assert ctx.active is False

        # 验证已存储
        traces = storage.query()
        assert len(traces) >= 1

    def test_span_context_manager(self, ctx):
        ctx.start_trace(TraceType.RETRIEVAL)
        with ctx.span("query_rewrite") as span:
            span.attributes["query"] = "test"
            assert span.name == "query_rewrite"

        # Span 结束时自动记录了 end_time
        assert span.end_time is not None
        ctx.end_trace()

    def test_span_error_handling(self, ctx):
        ctx.start_trace(TraceType.RETRIEVAL)
        try:
            with ctx.span("risky_operation") as span:
                raise ValueError("something wrong")
        except ValueError:
            pass
        assert span.status == SpanStatus.ERROR
        assert "error" in span.attributes
        ctx.end_trace(TraceStatus.FAILED)

    def test_nested_spans(self, ctx):
        ctx.start_trace(TraceType.INDEX)
        with ctx.span("parent"):
            with ctx.span("child") as child:
                child.attributes["depth"] = 1
        assert child.parent_id is not None
        ctx.end_trace()

    def test_record_event(self, ctx, storage):
        ctx.start_trace(TraceType.INDEX)
        ctx.record_event("chunk_created", {"count": 5})
        ctx.end_trace()
        # Event 通过 collector 存储

    def test_record_metric(self, ctx):
        ctx.start_trace(TraceType.RETRIEVAL)
        ctx.record_metric("latency_ms", 150.0)
        ctx.end_trace()

    def test_no_active_trace(self, ctx):
        # 没有活跃 Trace 时不应报错
        ctx.end_trace()  # 应该只是 warn
        assert ctx.active is False


# ═══════════════════════════════════════════════════
# Test 3: Storage 测试
# ═══════════════════════════════════════════════════

class TestMemoryTraceStorage:
    def test_save_and_get(self, storage):
        t = Trace(trace_type=TraceType.RETRIEVAL)
        storage.save(t)
        assert storage.get(t.id) is t

    def test_get_not_found(self, storage):
        assert storage.get("nonexistent") is None

    def test_save_span(self, storage):
        s = Span(trace_id="t1", name="test")
        storage.save_span(s)
        spans = storage.get_spans("t1")
        assert len(spans) == 1
        assert spans[0].name == "test"

    def test_save_metric(self, storage):
        m = Metric(trace_id="t1", metric_name="latency", value=100)
        storage.save_metric(m)
        metrics = storage.get_metrics("t1")
        assert len(metrics) == 1

    def test_query_by_type(self, storage):
        storage.save(Trace(trace_type=TraceType.RETRIEVAL))
        storage.save(Trace(trace_type=TraceType.INDEX))
        storage.save(Trace(trace_type=TraceType.RETRIEVAL))
        assert len(storage.query(trace_type=TraceType.RETRIEVAL)) == 2
        assert len(storage.query(trace_type=TraceType.INDEX)) == 1

    def test_delete(self, storage):
        t = Trace(trace_type=TraceType.RETRIEVAL)
        storage.save(t)
        s = Span(trace_id=t.id, name="span1")
        storage.save_span(s)
        assert storage.delete(t.id) is True
        assert storage.get(t.id) is None
        # 关联数据也应清理
        assert len(storage.get_spans(t.id)) == 0

    def test_clear(self, storage):
        storage.save(Trace(trace_type=TraceType.RETRIEVAL))
        storage.clear()
        assert len(storage.query()) == 0


# ═══════════════════════════════════════════════════
# Test 4: DefaultTraceCollector 测试
# ═══════════════════════════════════════════════════

class TestDefaultTraceCollector:
    def test_collect_trace(self, storage):
        collector = DefaultTraceCollector(storage=storage)
        t = Trace(trace_type=TraceType.RETRIEVAL)
        collector.collect(t)
        assert storage.get(t.id) is t

    def test_collect_span(self, storage):
        collector = DefaultTraceCollector(storage=storage)
        s = Span(trace_id="t1", name="test")
        collector.collect_span(s)
        spans = storage.get_spans("t1")
        assert len(spans) == 1


# ═══════════════════════════════════════════════════
# Test 5: Index Trace 测试
# ═══════════════════════════════════════════════════

class TestIndexPipelineTrace:
    def test_build_creates_trace(self):
        mgr = IndexPipelineManager(
            chunk_func=lambda doc: [{"id": "c1", "content": "hello"}],
        )
        doc = type("Doc", (), {"id": "d1", "content": "test"})()
        count = mgr.build(doc)
        assert count == 1

    def test_build_with_trace_context(self, storage):
        """Trace 通过 Collector 写入 Storage。"""
        collector = DefaultTraceCollector(storage=storage)
        ctx = TraceContext(collector=collector)

        mgr = IndexPipelineManager(
            chunk_func=lambda doc: [{"id": "c1", "content": "hello"}],
            trace_ctx=ctx,
        )
        doc = type("Doc", (), {"id": "d1", "content": "test"})()
        mgr.build(doc)

        # 验证 Trace 已存储
        traces = storage.query(trace_type=TraceType.INDEX)
        assert len(traces) == 1
        assert traces[0].metadata["document_id"] == "d1"

    def test_rebuild_produces_trace(self):
        mgr = IndexPipelineManager(
            chunk_func=lambda doc: [{"id": "c1", "content": "hello"}],
        )
        doc = type("Doc", (), {"id": "d1", "content": "test"})()
        count = mgr.rebuild(doc)
        assert count == 1

    def test_incremental_updates_trace(self):
        mgr = IndexPipelineManager()
        doc = type("Doc", (), {"id": "d1", "content": "test"})()
        count = mgr.incremental(doc, [{"id": "c1", "content": "changed"}])
        assert count == 1


# ═══════════════════════════════════════════════════
# Test 6: Retrieval Trace 测试
# ═══════════════════════════════════════════════════

class TestRetrievalPipelineTrace:
    def test_retrieval_returns_trace(self):
        """RetrievalPipelineV3 返回的 RetrievalTrace 应包含基本信息。"""
        from retrieval.pipeline_v3 import RetrievalPipelineV3
        pipeline = RetrievalPipelineV3()
        results, trace = pipeline.retrieve("test query", retriever_names=["vector"])
        assert trace.query == "test query"
        assert isinstance(trace.latency_ms, float)

    def test_pipeline_trace_integration(self, storage):
        """管线 + TraceContext 集成。"""
        from retrieval.pipeline_v3 import RetrievalPipelineV3

        collector = DefaultTraceCollector(storage=storage)
        ctx = TraceContext(collector=collector)

        # 使用带 Trace 的 pipeline
        pipeline = RetrievalPipelineV3(trace_ctx=ctx)
        results, rtrace = pipeline.retrieve("hello", retriever_names=["vector"])

        # Trace 应已存储
        traces = storage.query(trace_type=TraceType.RETRIEVAL)
        assert len(traces) == 1
        assert traces[0].metadata["query"] == "hello"


# ═══════════════════════════════════════════════════
# Test 7: Generation Trace 测试
# ═══════════════════════════════════════════════════

class TestGenerationTrace:
    def test_record_prompt(self, ctx):
        GenerationTrace.record_prompt(ctx, "user query", "system prompt")
        # 不应报错

    def test_record_response(self, ctx):
        GenerationTrace.record_response(ctx, "answer", "gpt-4")
        # 不应报错

    def test_record_usage(self, ctx):
        GenerationTrace.record_usage(ctx, prompt_tokens=50, completion_tokens=100)
        # 不应报错

    def test_full_generation_trace(self, ctx, storage):
        ctx._collector = DefaultTraceCollector(storage=storage)
        GenerationTrace.start_generation_trace(ctx, "test query", "gpt-4o-mini")
        GenerationTrace.record_prompt(ctx, "test query", "system")
        GenerationTrace.record_response(ctx, "answer text", "gpt-4o-mini")
        GenerationTrace.record_usage(ctx, prompt_tokens=10, completion_tokens=20)
        GenerationTrace.end_generation_trace(ctx)

        traces = storage.query(trace_type=TraceType.GENERATION)
        assert len(traces) == 1


# ═══════════════════════════════════════════════════
# Test 8: Evaluation Trace 测试
# ═══════════════════════════════════════════════════

class TestEvaluationTrace:
    def test_record_evaluation(self, ctx, storage):
        ctx._collector = DefaultTraceCollector(storage=storage)
        EvaluationTrace.record(
            ctx,
            dataset_name="test_dataset",
            strategy_name="hybrid",
            metrics={"recall@5": 0.92, "precision@5": 0.85},
        )
        traces = storage.query(trace_type=TraceType.EVALUATION)
        assert len(traces) == 1
        assert traces[0].metadata["dataset"] == "test_dataset"

        metrics = storage.get_metrics(traces[0].id)
        assert len(metrics) == 2


# ═══════════════════════════════════════════════════
# Test 9: TraceService 测试
# ═══════════════════════════════════════════════════

class TestTraceService:
    def test_query_traces(self, storage):
        svc = TraceService(storage=storage)
        assert svc.query_traces() == []

        storage.save(Trace(trace_type=TraceType.RETRIEVAL))
        assert len(svc.query_traces()) == 1

    def test_get_trace_detail_not_found(self, storage):
        svc = TraceService(storage=storage)
        assert svc.get_trace_detail("nonexistent") is None

    def test_get_trace_detail(self, storage):
        t = Trace(trace_type=TraceType.RETRIEVAL, metadata={"query": "hello"})
        storage.save(t)
        storage.save_span(Span(trace_id=t.id, name="rewrite"))
        storage.save_metric(Metric(trace_id=t.id, metric_name="latency_ms", value=100))

        svc = TraceService(storage=storage)
        detail = svc.get_trace_detail(t.id)
        assert detail is not None
        assert detail["trace_type"] == "retrieval"
        assert len(detail["spans"]) == 1
        assert len(detail["metrics"]) == 1

    def test_get_latency_metrics(self, storage):
        t = Trace(trace_type=TraceType.RETRIEVAL)
        storage.save(t)
        storage.save_metric(Metric(trace_id=t.id, metric_name="latency_ms", value=200))

        svc = TraceService(storage=storage)
        metrics = svc.get_latency_metrics()
        assert len(metrics) >= 1
        assert metrics[0]["latency_ms"] == 200

    def test_get_dashboard_summary(self, storage):
        for _ in range(3):
            t = Trace(trace_type=TraceType.RETRIEVAL)
            storage.save(t)
            storage.save_metric(Metric(trace_id=t.id, metric_name="latency_ms", value=100))

        svc = TraceService(storage=storage)
        summary = svc.get_dashboard_summary()
        assert summary["retrieval_count"] == 3
        assert summary["avg_retrieval_latency_ms"] == 100

    def test_get_index_traces(self, storage):
        t = Trace(trace_type=TraceType.INDEX, metadata={"document_id": "doc_1"})
        storage.save(t)

        svc = TraceService(storage=storage)
        results = svc.get_index_traces("doc_1")
        assert len(results) == 1

    def test_get_retrieval_analysis(self, storage):
        t = Trace(trace_type=TraceType.RETRIEVAL, metadata={"query": "test"})
        storage.save(t)
        storage.save_metric(Metric(trace_id=t.id, metric_name="latency_ms", value=100))
        storage.save_metric(Metric(trace_id=t.id, metric_name="result_count", value=5))

        svc = TraceService(storage=storage)
        analysis = svc.get_retrieval_analysis()
        assert len(analysis) >= 1
        assert analysis[0]["query"] == "test"
        assert analysis[0]["result_count"] == 5


# ═══════════════════════════════════════════════════
# Test 10: IndexRecord 增强字段测试
# ═══════════════════════════════════════════════════

def test_index_record_enhanced_fields():
    """IndexRecord 包含 v0.3 Phase 2 新增字段。"""
    record = IndexRecord(
        document_id="doc_1",
        index_version="v2",
        content_hash="abc123",
        chunk_strategy="recursive",
        embedding_dimension=1024,
        vector_store="milvus",
        build_duration=3.5,
    )
    assert record.index_version == "v2"
    assert record.content_hash == "abc123"
    assert record.chunk_strategy == "recursive"
    assert record.embedding_dimension == 1024
    assert record.vector_store == "milvus"
    assert record.build_duration == 3.5


# ═══════════════════════════════════════════════════
# Test 11: 端到端集成测试
# ═══════════════════════════════════════════════════

def test_end_to_end_trace_flow():
    """完整流程：Retrieval -> Trace -> Storage -> Service 查询。"""
    storage = MemoryTraceStorage()
    collector = DefaultTraceCollector(storage=storage)
    ctx = TraceContext(collector=collector)

    # 1. 执行检索（模拟）
    ctx.start_trace(
        TraceType.RETRIEVAL,
        request_id="req-001",
        metadata={"query": "what is RAG?", "top_k": 5},
    )

    with ctx.span("query_rewrite", original_query="what is RAG?"):
        pass

    with ctx.span("vector_search", strategy="vector", top_k=5):
        ctx.record_metric("result_count", 5)

    with ctx.span("fusion", method="rrf") as sp:
        sp.attributes["input_count"] = 2
        sp.attributes["output_count"] = 5

    ctx.record_metric("latency_ms", 85.3)
    ctx.record_event("cache_hit", {"cache_type": "embedding"})
    ctx.end_trace(TraceStatus.SUCCESS)

    # 2. 通过 Service 查询
    svc = TraceService(storage=storage)
    traces = svc.query_traces(trace_type=TraceType.RETRIEVAL)
    assert len(traces) == 1

    detail = svc.get_trace_detail(traces[0]["trace_id"])
    assert detail is not None
    assert len(detail["spans"]) == 3
    # 2 个指标: result_count + latency_ms
    assert len(detail["metrics"]) == 2
    assert "what is RAG?" in detail["metadata"]["query"]

    summary = svc.get_dashboard_summary()
    assert summary["retrieval_count"] >= 1
    assert summary["avg_retrieval_latency_ms"] > 0
