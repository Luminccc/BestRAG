"""ProviderFactory + Registry 集成测试。"""

from core.registry import get_registry
from core.registry.center import reset_registry
from core.provider import ProviderFactory, JaccardSimilarityProvider


class TestProviderFactory:
    """ProviderFactory 测试。"""

    def setup_method(self):
        reset_registry()

    def test_create_similarity_jaccard(self):
        factory = ProviderFactory()
        provider = factory.create_similarity("jaccard")
        assert isinstance(provider, JaccardSimilarityProvider)
        assert provider.name == "jaccard"
        sim = provider.similarity("hello world", "hello world")
        assert sim == 1.0

    def test_create_similarity_cosine(self):
        factory = ProviderFactory()
        provider = factory.create_similarity("cosine")
        assert provider.name == "cosine"

    def test_create_similarity_invalid(self):
        factory = ProviderFactory()
        try:
            factory.create_similarity("invalid")
            assert False, "should raise ValueError"
        except ValueError:
            pass

    def test_register_provider(self):
        ProviderFactory.register_provider(
            "similarity", "jaccard", JaccardSimilarityProvider
        )
        rc = get_registry()
        assert rc.strategy.has("similarity:jaccard")
