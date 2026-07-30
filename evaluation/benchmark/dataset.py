"""EvaluationDataset — 评测数据集。"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set


@dataclass
class EvalSample:
    """单个评测样本。

    Attributes:
        query:        查询文本。
        expected_ids: 期望的文档/Chunk ID 集合。
        metadata:     额外信息（场景、难度等）。
    """
    query: str
    expected_ids: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EvaluationDataset:
    """评测数据集。

    包含多个评测样本，按场景分组。

    用法::

        dataset = EvaluationDataset(name="tech_docs")
        dataset.add_sample(EvalSample(query="如何配置?", expected_ids={"doc1"}))
    """

    def __init__(self, name: str = "", samples: List[EvalSample] | None = None):
        self.name = name
        self._samples: List[EvalSample] = list(samples) if samples else []

    def add_sample(self, sample: EvalSample) -> None:
        self._samples.append(sample)

    @property
    def samples(self) -> List[EvalSample]:
        return list(self._samples)

    @property
    def size(self) -> int:
        return len(self._samples)
