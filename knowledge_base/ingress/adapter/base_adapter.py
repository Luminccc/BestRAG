"""BaseAdapter — 所有 Adapter 的抽象基类。

所有 Adapter 通过 ``load()`` 返回 InputFile（或 list[InputFile]）。
子类构造器接受 Source 对象（或保持向后兼容的原始参数）。
"""

from abc import ABC, abstractmethod

from ..model.input_file import InputFile


class BaseAdapter(ABC):
    """单文件 Adapter 抽象契约。

    每个来源类型（upload, local, github, ...）必须实现此基类。
    """

    @abstractmethod
    def load(self) -> InputFile:
        """返回单个 InputFile。"""
        ...


class BaseBatchAdapter(ABC):
    """批量 Adapter 抽象契约（folder, github repo, ...）。"""

    @abstractmethod
    def load(self) -> list[InputFile]:
        """返回 InputFile 列表。"""
        ...
