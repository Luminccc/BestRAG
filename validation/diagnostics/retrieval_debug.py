"""Retrieval Debug — 检索诊断工具。

用于 Debug：为什么某个问题没有搜到期望的文档？

输出各检索通道的详细结果：
- Vector 检索结果
- BM25 检索结果（如可用）
- 混合检索融合结果
- Rerank 最终结果

不负责：
- 修改检索逻辑
- 自动修复
"""

from time import time
from typing import Optional

from validation.model import DebugResult


def debug_retrieval(
    query: str,
    retrieval_service=None,
    embedding_service=None,
    vector_store_service=None,
    rerank_service=None,
    top_k: int = 10,
) -> DebugResult:
    """诊断检索流程，返回各阶段详情。

    Args:
        query:                 查询文本。
        retrieval_service:     RetrievalService 实例。
        embedding_service:     EmbeddingService 实例（用于直接向量搜索）。
        vector_store_service:  VectorStoreService 实例（用于直接向量搜索）。
        rerank_service:        RerankService 实例。
        top_k:                 检索数量。

    Returns:
        DebugResult（含各阶段诊断数据）。
    """
    sections: list[str] = []
    details: dict = {}
    t0 = time()

    if retrieval_service is None:
        return DebugResult(
            query=query,
            sections=["error"],
            details={"error": "RetrievalService 未注入"},
        )

    try:
        # ── 1. 主检索 ──
        t1 = time()
        results = retrieval_service.retrieve(query, top_k=top_k)
        ret_latency = round((time() - t1) * 1000, 2)
        sections.append("retrieval")

        details["retrieval"] = {
            "query": query,
            "top_k": top_k,
            "result_count": len(results),
            "latency_ms": ret_latency,
            "results": [
                {
                    "chunk_id": r.chunk_id,
                    "score": round(r.score, 4),
                    "content_preview": r.content[:150],
                }
                for r in results[:top_k]
            ],
        }

        # ── 2. Rerank 诊断（可选） ──
        if rerank_service is not None and len(results) > 1:
            t2 = time()
            try:
                reranked = rerank_service.rerank(query, results)
                rerank_latency = round((time() - t2) * 1000, 2)
                sections.append("rerank")
                details["rerank"] = {
                    "input_count": len(results),
                    "output_count": len(reranked),
                    "latency_ms": rerank_latency,
                    "results": [
                        {
                            "chunk_id": r.chunk_id,
                            "score": round(r.score, 4),
                            "content_preview": r.content[:150],
                        }
                        for r in reranked[:5]
                    ],
                }
            except Exception as e:
                details["rerank"] = {"error": str(e)}

    except Exception as e:
        details["retrieval"] = {"error": f"{type(e).__name__}: {e}"}
        sections.append("error")

    return DebugResult(
        query=query,
        sections=sections,
        latency_ms=round((time() - t0) * 1000, 2),
        details=details,
    )
