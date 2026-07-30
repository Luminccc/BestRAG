"""RAGProfile 模型测试。"""

from optimization.profile.model import RAGProfile, DEFAULT_PROFILE, TECHNICAL_DOC_PROFILE


class TestRAGProfile:
    """RAGProfile 测试。"""

    def test_default_profile(self):
        p = RAGProfile()
        assert p.chunk_strategy == "recursive"
        assert p.retrieval_strategies == ["vector"]

    def test_custom_profile(self):
        p = RAGProfile(
            name="custom",
            chunk_strategy="semantic",
            retrieval_strategies=["vector", "bm25"],
            fusion_strategy="rrf",
        )
        assert p.name == "custom"
        assert p.chunk_strategy == "semantic"

    def test_to_dict(self):
        p = TECHNICAL_DOC_PROFILE
        d = p.to_dict()
        assert d["name"] == "technical_doc"
        assert "chunk_strategy" in d
        assert "fusion_strategy" in d

    def test_builtin_profiles(self):
        assert DEFAULT_PROFILE.name == "default"
        assert TECHNICAL_DOC_PROFILE.chunk_strategy == "heading"
