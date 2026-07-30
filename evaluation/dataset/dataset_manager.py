"""DatasetManager — 评测数据集管理。

支持创建、版本管理和导入导出。
基于现有 EvaluationDataset 扩展。
"""

import json
from typing import Any, Dict, List, Optional

from core.logger import get_logger
from evaluation.benchmark.dataset import EvalSample, EvaluationDataset

logger = get_logger("evaluation.dataset")


class DatasetManager:
    """评测数据集管理器。

    Usage::

        mgr = DatasetManager()
        ds = mgr.create_dataset("tech_qa_v1", samples=[...])
        mgr.save_dataset(ds, "datasets/tech_qa_v1.json")
        loaded = mgr.load_dataset("datasets/tech_qa_v1.json")
    """

    def __init__(self):
        self._datasets: Dict[str, EvaluationDataset] = {}

    def create_dataset(
        self,
        name: str,
        samples: Optional[List[EvalSample]] = None,
    ) -> EvaluationDataset:
        """创建数据集。"""
        ds = EvaluationDataset(name=name, samples=samples)
        self._datasets[name] = ds
        logger.info(f"数据集创建: {name}")
        return ds

    def get_dataset(self, name: str) -> Optional[EvaluationDataset]:
        """获取数据集。"""
        return self._datasets.get(name)

    def list_datasets(self) -> List[str]:
        """列出所有数据集。"""
        return list(self._datasets.keys())

    def add_sample(self, dataset_name: str, sample: EvalSample) -> None:
        """添加样本到数据集。"""
        ds = self.get_dataset(dataset_name)
        if ds is None:
            raise ValueError(f"数据集不存在: {dataset_name}")
        ds.add_sample(sample)

    def create_version(self, base_name: str, version: str) -> EvaluationDataset:
        """创建数据集版本。

        Usage::

            ds_v2 = mgr.create_version("tech_qa", "v2")
        """
        name = f"{base_name}_{version}"
        ds = EvaluationDataset(name=name)
        self._datasets[name] = ds
        logger.info(f"数据集版本创建: {name}")
        return ds

    # ── 导入导出 ──────────────────────────────────

    @staticmethod
    def save_dataset(dataset: EvaluationDataset, path: str) -> None:
        """导出数据集到 JSON 文件。"""
        data = {
            "name": dataset.name,
            "samples": [
                {
                    "query": s.query,
                    "expected_ids": list(s.expected_ids),
                    "metadata": s.metadata,
                }
                for s in dataset.samples
            ],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"数据集已导出: {path}")

    @staticmethod
    def load_dataset(path: str) -> EvaluationDataset:
        """从 JSON 文件导入数据集。"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        ds = EvaluationDataset(name=data.get("name", "imported"))
        for s in data.get("samples", []):
            ds.add_sample(EvalSample(
                query=s["query"],
                expected_ids=set(s.get("expected_ids", [])),
                metadata=s.get("metadata", {}),
            ))
        logger.info(f"数据集已导入: {path}")
        return ds

    @staticmethod
    def export_to_dict(dataset: EvaluationDataset) -> Dict[str, Any]:
        """导出数据集到字典。"""
        return {
            "name": dataset.name,
            "size": dataset.size,
            "samples": [
                {"query": s.query, "expected_ids": list(s.expected_ids)}
                for s in dataset.samples
            ],
        }
