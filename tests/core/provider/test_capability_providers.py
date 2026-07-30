"""Embedding / Reranker / LLM Provider 接口测试。"""

import pytest

from core.provider import (
    BaseEmbeddingProvider,
    BaseRerankerProvider,
    BaseLLMProvider,
)


class TestEmbeddingProvider:
    """Embedding Provider 接口测试。"""

    def test_base_is_abstract(self):
        """BaseEmbeddingProvider 不能直接实例化。"""
        with pytest.raises(TypeError):
            BaseEmbeddingProvider()  # type: ignore

    def test_concrete_embedding_provider(self):
        class TestEmbed(BaseEmbeddingProvider):
            name = "test_embed"
            def embed(self, texts):
                return [[0.1]] * len(texts)
            def embed_text(self, text):
                return [0.1, 0.2]
            @property
            def dimension(self):
                return 2

        p = TestEmbed()
        assert p.name == "test_embed"
        assert p.embed(["hello"]) == [[0.1]]
        assert p.embed_text("hello") == [0.1, 0.2]
        assert p.dimension == 2


class TestRerankerProvider:
    """Reranker Provider 接口测试。"""

    def test_base_is_abstract(self):
        with pytest.raises(TypeError):
            BaseRerankerProvider()  # type: ignore

    def test_concrete_reranker_provider(self):
        class TestRerank(BaseRerankerProvider):
            name = "test_rerank"
            def rerank(self, query, documents):
                return documents

        p = TestRerank()
        docs = [{"id": 1}]
        result = p.rerank("query", docs)
        assert result == docs


class TestLLMProvider:
    """LLM Provider 接口测试。"""

    def test_base_is_abstract(self):
        with pytest.raises(TypeError):
            BaseLLMProvider()  # type: ignore

    def test_concrete_llm_provider(self):
        class TestLLM(BaseLLMProvider):
            name = "test_llm"
            def generate(self, messages, **kwargs):
                return "generated response"

        p = TestLLM()
        result = p.generate([{"role": "user", "content": "hi"}])
        assert result == "generated response"
