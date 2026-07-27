"""Generation Domain Integration Test — 验证 Generation v1.0 验收标准。

运行方式::

    uv run pytest tests/test_generation_integration.py -v

TC-001 Provider     TC-004 Pipeline
TC-002 Config       TC-005 OpenAI Compatible
TC-003 Prompt
"""

from unittest.mock import MagicMock, patch

import pytest

from core.config import ConfigManager, GenerationConfig
from core.registry import ServiceRegistry
from generation.context.builder import ContextBuilder
from generation.exception import ProviderError
from generation.model import GenerationRequest, GenerationResponse
from generation.pipeline import GenerationPipeline
from generation.prompt.builder import PromptBuilder
from generation.provider.base import BaseLLMProvider
from generation.provider.openai_compatible import OpenAICompatibleProvider
from generation.service import GenerationService
from retrieval.retriever.model import RetrievalResult


# ═══════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _reset():
    ConfigManager().reset()
    ServiceRegistry().clear()
    yield
    ConfigManager().reset()
    ServiceRegistry().clear()


@pytest.fixture
def sample_results():
    """模拟 RetrievalResult 列表。"""
    return [
        RetrievalResult(chunk_id="1", score=0.95, content="RAG框架需要向量数据库和Embedding模型支持。", metadata={}),
        RetrievalResult(chunk_id="2", score=0.88, content="部署时需注意Milvus的端口配置和索引参数。", metadata={}),
        RetrievalResult(chunk_id="3", score=0.70, content="推荐使用BGE-M3作为Embedding模型。", metadata={}),
    ]


# ═══════════════════════════════════════════════════
# TC-001: Provider initialize
# ═══════════════════════════════════════════════════

class _MockProvider(BaseLLMProvider):
    """模拟 LLM Provider。"""
    def generate(self, messages, **kwargs):
        return "这是模拟的回答：基于上述文档，您需要..."


def test_provider_generate():
    """LLM Provider generate() 返回字符串。"""
    provider = _MockProvider()
    answer = provider.generate([{"role": "user", "content": "如何部署RAG?"}])
    assert isinstance(answer, str)
    assert len(answer) > 0


# ═══════════════════════════════════════════════════
# TC-002: Config
# ═══════════════════════════════════════════════════

def test_generation_config_defaults():
    """GenerationConfig 默认值正确。"""
    cfg = ConfigManager().get()
    assert cfg.generation.provider == "openai"
    assert cfg.generation.model_name == "gpt-4o-mini"
    assert cfg.generation.temperature == 0.2
    assert cfg.generation.base_url == "https://api.openai.com/v1"


def test_generation_config_env_override(monkeypatch):
    """环境变量覆盖有效。"""
    monkeypatch.setenv("BESTRAG_LLM_MODEL", "deepseek-chat")
    monkeypatch.setenv("BESTRAG_LLM_BASE_URL", "https://api.deepseek.com")

    ConfigManager().reset()
    cfg = ConfigManager().get()
    assert cfg.generation.model_name == "deepseek-chat"
    assert cfg.generation.base_url == "https://api.deepseek.com"


# ═══════════════════════════════════════════════════
# TC-003: Prompt
# ═══════════════════════════════════════════════════

def test_prompt_builder_default():
    """默认 system prompt + context → messages。"""
    builder = PromptBuilder()
    messages = builder.build("如何部署?", "[Document 1]\nRAG部署指南")

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "企业知识助手" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert "如何部署?" in messages[1]["content"]
    assert "[Document 1]" in messages[1]["content"]


def test_prompt_builder_custom_system():
    """自定义 system prompt 优先于默认。"""
    builder = PromptBuilder()
    messages = builder.build("问", "上下文", system_prompt="你是一个技术专家")

    assert "技术专家" in messages[0]["content"]


def test_prompt_builder_empty_context():
    """无 context 时 user 消息不含参考文档。"""
    builder = PromptBuilder()
    messages = builder.build("提问", "")
    assert "参考文档" not in messages[1]["content"]


# ═══════════════════════════════════════════════════
# TC-004: Pipeline
# ═══════════════════════════════════════════════════

def test_pipeline_with_retrieval_results(sample_results):
    """Pipeline: results → Context → Prompt → Mock LLM → Answer。"""
    mock_llm = _MockProvider()
    pipeline = GenerationPipeline(llm_provider=mock_llm)

    response = pipeline.generate(
        query="如何部署RAG?",
        results=sample_results,
        system_prompt="你是企业知识助手",
    )

    assert isinstance(response, GenerationResponse)
    assert len(response.answer) > 0
    assert "模拟的回答" in response.answer


def test_pipeline_with_text_context():
    """Pipeline: 直接传 context 字符串。"""
    mock_llm = _MockProvider()
    pipeline = GenerationPipeline(llm_provider=mock_llm)

    response = pipeline.generate(
        query="如何部署RAG?",
        context="[Document 1]\nRAG部署需要Milvus和BGE模型。",
    )

    assert response.answer
    assert len(response.sources) == 1


# ═══════════════════════════════════════════════════
# TC-005: OpenAI Compatible
# ═══════════════════════════════════════════════════

def test_openai_compatible_config_switching():
    """Provider 读取配置中的 base_url/api_key/model。"""
    cfg = ConfigManager().get()
    cfg.generation.base_url = "https://api.deepseek.com"
    cfg.generation.api_key = "sk-test-key"
    cfg.generation.model_name = "deepseek-chat"

    # 不实际调用 LLM，只验证 provider 构造时读到了正确配置
    provider = OpenAICompatibleProvider()
    assert provider._base_url == "https://api.deepseek.com"
    assert provider._api_key == "sk-test-key"
    assert provider._model == "deepseek-chat"


def test_context_builder(sample_results):
    """ContextBuilder: 去重 + 编号 + 长度限制。"""
    builder = ContextBuilder(max_length=500)
    context = builder.build(sample_results)

    assert "[Document 1]" in context
    assert "[Document 2]" in context
    assert "[Document 3]" in context
    # 无重复
    assert context.count("[Document 1]") == 1


def test_context_builder_deduplicate():
    """重复 chunk_id 去重。"""
    results = [
        RetrievalResult(chunk_id="dup", score=0.9, content="AAA", metadata={}),
        RetrievalResult(chunk_id="dup", score=0.8, content="AAA", metadata={}),
    ]
    builder = ContextBuilder()
    context = builder.build(results)
    assert "[Document 2]" not in context


def test_service_layer(sample_results):
    """GenerationService 封装 Pipeline。"""
    mock_llm = _MockProvider()
    pipeline = GenerationPipeline(llm_provider=mock_llm)
    svc = GenerationService(pipeline=pipeline)

    response = svc.generate("如何部署RAG?", results=sample_results)
    assert isinstance(response, GenerationResponse)
    assert "模拟的回答" in response.answer
