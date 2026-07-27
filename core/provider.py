"""Provider 基类 — 定义统一资源生命周期。

所有 Provider（Embedding / VectorStore / Reranker / Parser / LLM）
必须实现此接口。Core 通过 initialize() / close() 管理 Provider 生命周期。

生命周期::

    create → initialize → use → close
"""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Provider 抽象契约。

    每个 Provider 封装一个可管理的服务/资源实例。
    """

    @abstractmethod
    def initialize(self) -> None:
        """初始化 Provider（加载模型、建立连接、预热等）。

        Raises:
            ProviderError: 初始化失败。
        """
        ...

    @abstractmethod
    def close(self) -> None:
        """释放 Provider 持有的资源（关闭连接、卸载模型）。

        调用后 Provider 不应再被使用。
        """
        ...
