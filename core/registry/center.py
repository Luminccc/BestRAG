"""RegistryCenter — 统一注册中心入口。

聚合六大 Registry，提供全局访问点。

用法::

    from core.registry.center import RegistryCenter, get_registry

    rc = RegistryCenter()
    rc.service.register("document", DocumentService(...))
    rc.strategy.register("semantic", SemanticChunkStrategy)
    rc.provider.register("llm", LLMProvider(...))
    rc.evaluator.register("recall", RecallEvaluator)
    rc.model.register("knowledge_base", KnowledgeBase)
    rc.repository.register("document", DocumentRepository(...))
"""

from core.registry.service import ServiceRegistry
from core.registry.strategy import StrategyRegistry
from core.registry.provider import ProviderRegistry
from core.registry.evaluator import EvaluatorRegistry
from core.registry.model import ModelRegistry
from core.registry.repository import RepositoryRegistry


class RegistryCenter:
    """统一注册中心，聚合六类注册表。

    属性:
        service    : ServiceRegistry     — 运行时服务
        strategy   : StrategyRegistry    — 策略插件
        provider   : ProviderRegistry    — Provider 实例
        evaluator  : EvaluatorRegistry   — 评估器类
        model      : ModelRegistry       — v0.3 模型类
        repository : RepositoryRegistry  — v0.3 数据仓库
    """

    def __init__(self):
        self.service = ServiceRegistry()
        self.strategy = StrategyRegistry()
        self.provider = ProviderRegistry()
        self.evaluator = EvaluatorRegistry()
        self.model = ModelRegistry()
        self.repository = RepositoryRegistry()

    # ── 批量操作 ──────────────────────────────────

    def clear_all(self) -> None:
        """清空所有注册（应用 shutdown 时调用）。"""
        self.service.clear()
        self.strategy.clear()
        self.provider.clear()
        self.evaluator.clear()
        self.model.clear()
        self.repository.clear()


# ═══════════════════════════════════════════════════
# 全局单例
# ═══════════════════════════════════════════════════

_registry_center: RegistryCenter | None = None


def get_registry() -> RegistryCenter:
    """获取全局 RegistryCenter 实例（懒创建）。

    用途::

        from core.registry import get_registry
        rc = get_registry()
        rc.strategy.get("semantic")
    """
    global _registry_center
    if _registry_center is None:
        _registry_center = RegistryCenter()
    return _registry_center


def reset_registry() -> None:
    """重置全局 RegistryCenter（测试用）。"""
    global _registry_center
    _registry_center = None
