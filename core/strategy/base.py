"""BaseStrategy — 所有策略的抽象基类。

所有策略必须：
1. 继承 BaseStrategy
2. 设置 name 属性
3. 实现 execute 方法

生命周期::

    strategy = SomeStrategy()
    strategy.initialize()   # 可选初始化
    result = strategy.execute(input)
    strategy.close()        # 可选清理
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseStrategy(ABC):
    """策略基类。

    属性:
        name: 策略名称，用于 Registry 标识。
    """

    name: str = ""

    def initialize(self) -> None:
        """初始化资源（可选覆盖）。"""

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """执行策略核心逻辑。"""

    def close(self) -> None:
        """释放资源（可选覆盖）。"""
