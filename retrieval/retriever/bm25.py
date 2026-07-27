"""BM25Retriever — 关键词检索策略。

基于 rank_bm25 实现 BM25 关键词检索。
索引时（indexing 域）同步注册文档到 BM25 corpus，
检索时对 corpus 做关键词匹配。

注意：BM25 corpus 在内存中维护，重启后需重新构建。
可在 Indexing 写入 VectorStore 后调用 register_corpus() 同步。
"""

import re
from typing import Any, Dict, List, Optional

from core.logger import get_logger
from rank_bm25 import BM25Okapi

from retrieval.retriever.model import RetrievalResult

logger = get_logger(__name__)


# ── 全角 / 半角标点集合 ──────────────────────────

# 全角 / 半角标点集合（含空白字符）
_RE_NON_CHAR = re.compile(
    r'[，。！？；：、""''（）【】《》 \t\n\r\f\v,.!?;:\"' + r"'()\[\]{}]+"
)

# ── 全局 corpus（本进程内共享）──────────────────

_corpus: List[str] = []           # 文档文本（分词后）
_corpus_chunks: List[Dict] = []    # chunk_id / content / metadata 原始信息
_bm25: Optional[BM25Okapi] = None


def _tokenize(text: str) -> List[str]:
    """中英文混合分词：中文按字符切分，英文按空格切分，去除标点。"""
    # 先按英文空格粗略拆分
    parts: List[str] = []
    for part in text.lower().split():
        # 每个部分按标点再次拆分
        sub_parts = _RE_NON_CHAR.split(part)
        for sp in sub_parts:
            sp = sp.strip()
            if not sp:
                continue
            # 纯中文：逐字切分
            if re.search(r"[一-鿿]", sp):
                parts.extend(list(sp))
            else:
                parts.append(sp)
    return parts


def register_corpus(chunks: List[Dict[str, Any]]) -> None:
    """注册 BM25 corpus（通常在 Indexing 完成 VectorStore 写入后调用）。

    Args:
        chunks: 字典列表，每个含 chunk_id / content / metadata。
    """
    global _corpus, _corpus_chunks, _bm25
    _corpus_chunks = list(chunks)
    _corpus = [_tokenize(c["content"]) for c in chunks]
    _bm25 = BM25Okapi(_corpus)
    logger.info(f"BM25 corpus 已注册: {len(_corpus)} 条文档")


def clear_corpus() -> None:
    """清空 BM25 corpus。"""
    global _corpus, _corpus_chunks, _bm25
    _corpus.clear()
    _corpus_chunks.clear()
    _bm25 = None


class BM25Retriever:
    """BM25 关键词检索 — 对已注册 corpus 进行 BM25 评分。"""

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalResult]:
        """执行 BM25 检索。

        Args:
            query:   查询文本。
            top_k:   返回结果数量。
            filters: 元数据过滤条件。

        Returns:
            检索结果列表。
        """
        global _bm25, _corpus_chunks

        if _bm25 is None:
            logger.warning("BM25 corpus 为空，返回空结果")
            return []

        tokenized_query = _tokenize(query)
        scores = _bm25.get_scores(tokenized_query)

        # 按分数降序取 top_k
        indexed = [(i, scores[i]) for i in range(len(scores))]
        indexed.sort(key=lambda x: x[1], reverse=True)
        top = indexed[:top_k]

        results: List[RetrievalResult] = []
        for idx, score in top:
            if score <= 0:
                continue
            info = _corpus_chunks[idx]
            # 过滤
            if filters and not _match_filter(info.get("metadata", {}), filters):
                continue
            results.append(RetrievalResult(
                chunk_id=info["chunk_id"],
                score=float(score),
                content=info["content"],
                metadata=info.get("metadata", {}),
            ))

        logger.info(f"BM25Retriever 返回 {len(results)} 条结果")
        return results


def _match_filter(metadata: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
    """检查 metadata 是否匹配过滤条件。"""
    for key, expected in conditions.items():
        actual = metadata.get(key)
        if actual is None or str(actual) != str(expected):
            return False
    return True
