"""RAGProfile — RAG 策略组合配置。

定义 Chunk/Retrieval/Fusion/Query 等策略的组合，
表示一个完整的 RAG Pipeline 配置。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class RAGProfile:
    """RAG 策略组合配置。

    Attributes:
        name:                Profile 名称。
        description:         适用场景描述。
        chunk_strategy:      Chunk 策略名（如 "hierarchical", "semantic"）。
        retrieval_strategies: 检索器列表（如 ["vector", "bm25"]）。
        fusion_strategy:     融合策略名（如 "rrf", "weighted"）。
        query_strategy:      查询重写策略（如 "simple", "llm"）。
        reranker:            Reranker 名称（如 "bge"）。
        metadata_filter:     是否启用元数据过滤。
        metadata:            扩展元数据。
    """
    name: str = ""
    description: str = ""
    chunk_strategy: str = "recursive"
    retrieval_strategies: List[str] = field(default_factory=lambda: ["vector"])
    fusion_strategy: str = "rrf"
    query_strategy: str = "simple"
    reranker: str = ""
    metadata_filter: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "chunk_strategy": self.chunk_strategy,
            "retrieval_strategies": list(self.retrieval_strategies),
            "fusion_strategy": self.fusion_strategy,
            "query_strategy": self.query_strategy,
            "reranker": self.reranker,
            "metadata_filter": self.metadata_filter,
        }


# ── 内置 Profile 预设 ──────────────────────────────

# 通用默认配置
DEFAULT_PROFILE = RAGProfile(
    name="default",
    description="通用默认配置",
    chunk_strategy="recursive",
    retrieval_strategies=["vector"],
    fusion_strategy="rrf",
)

# 技术文档
TECHNICAL_DOC_PROFILE = RAGProfile(
    name="technical_doc",
    description="技术文档：标题切分 + 混合检索 + RRF",
    chunk_strategy="heading",
    retrieval_strategies=["vector", "bm25"],
    fusion_strategy="rrf",
    reranker="bge",
)

# FAQ 知识库
FAQ_PROFILE = RAGProfile(
    name="faq",
    description="FAQ：固定切分 + BM25 + 加权融合",
    chunk_strategy="fixed",
    retrieval_strategies=["vector", "bm25"],
    fusion_strategy="weighted",
)

# 长文档报告
LONG_DOC_PROFILE = RAGProfile(
    name="long_doc",
    description="长文档：层级切分 + 元数据检索 + 上下文窗口",
    chunk_strategy="hierarchical",
    retrieval_strategies=["vector", "metadata"],
    fusion_strategy="rrf",
    query_strategy="llm",
)

# 论文/学术
PAPER_PROFILE = RAGProfile(
    name="paper",
    description="论文：语义切分 + 向量检索 + RRF",
    chunk_strategy="semantic",
    retrieval_strategies=["vector", "bm25"],
    fusion_strategy="rrf",
)
