"""BaseProvider 生命周期测试。"""

from core.provider import BaseProvider


class _SimpleProvider(BaseProvider):
    name: str = "simple"


class TestBaseProvider:
    """BaseProvider 生命周期测试。"""

    def test_default_name(self):
        p = _SimpleProvider()
        assert p.name == "simple"

    def test_lifecycle_methods_have_defaults(self):
        p = _SimpleProvider()
        p.initialize()  # should not raise
        p.close()       # should not raise

    def test_custom_name(self):
        class CustomProvider(BaseProvider):
            name: str = "custom"
        p = CustomProvider()
        assert p.name == "custom"
