"""QAService — RAG 问答服务。

提供完整 RAG 问答能力：
- ask: 用户提问 → 检索 → 生成 → 回答

内部调用：
    RetrievalService → RerankService → GenerationService
"""

from time import time

from core.logger import get_logger
from features.model import QARequest, QAResponse

logger = get_logger("features.qa")


class QAService:
    """RAG 问答服务。

    Usage::

        svc = QAService(
            retrieval_service=retrieval_svc,
            generation_service=generation_svc,
            rerank_service=rerank_svc,
        )
        response = svc.ask(QARequest(query="如何部署系统？"))
    """

    def __init__(
        self,
        retrieval_service=None,   # RetrievalService
        generation_service=None,  # GenerationService
        rerank_service=None,      # RerankService（可选）
    ):
        self._retrieval = retrieval_service
        self._generation = generation_service
        self._rerank = rerank_service

    # ── 公开接口 ──────────────────────────────────

    def ask(self, request: QARequest) -> QAResponse:
        """执行 RAG 问答。

        流程：
            1. Retrieval 检索相关文档
            2. Rerank 重排序（可选）
            3. Generation 生成回答

        Args:
            request: 包含查询和参数的 QARequest。

        Returns:
            QAResponse（含 answer / sources / latency）。
        """
        total_start = time()
        sources: list[dict] = []
        context: str = ""
        retrieval_time = 0.0
        generation_time = 0.0

        # ── Step 1: Retrieval ──
        if self._retrieval is None:
            return QAResponse(answer="[错误] RetrievalService 未注入")

        t0 = time()
        try:
            results = self._retrieval.retrieve(request.query, top_k=request.top_k)
            retrieval_time = round((time() - t0) * 1000, 2)

            if not results:
                return QAResponse(
                    answer="未找到相关文档，请尝试其他问题或先上传知识库文档。",
                    retrieval_time=retrieval_time,
                    total_time=retrieval_time,
                )

            sources = [
                {
                    "chunk_id": r.chunk_id,
                    "score": round(r.score, 4),
                    "content": r.content[:300],
                    "metadata": r.metadata,
                }
                for r in results
            ]
            logger.info(f"检索完成: {len(results)} results, {retrieval_time}ms")
        except Exception as e:
            retrieval_time = round((time() - t0) * 1000, 2)
            return QAResponse(
                answer=f"[检索失败] {type(e).__name__}: {e}",
                retrieval_time=retrieval_time,
                total_time=retrieval_time,
            )

        # ── Step 2: Rerank（可选） ──
        reranked = results
        if self._rerank is not None and len(results) > 1:
            try:
                t0 = time()
                reranked = self._rerank.rerank(request.query, results)
                rerank_ms = round((time() - t0) * 1000, 2)
                logger.info(f"重排序完成: {len(reranked)} results, {rerank_ms}ms")
            except Exception as e:
                logger.warning(f"重排序失败（继续使用原始结果）: {e}")

        # ── Step 3: Generation ──
        if self._generation is None:
            return QAResponse(
                answer="[错误] GenerationService 未注入",
                sources=sources,
                retrieval_time=retrieval_time,
                total_time=round((time() - total_start) * 1000, 2),
            )

        # 构建 context
        context_parts = []
        for i, r in enumerate(reranked[:5]):
            context_parts.append(f"[Document {i + 1}]\n{r.content}")
        context = "\n\n".join(context_parts)

        t0 = time()
        try:
            response = self._generation.generate(
                query=request.query,
                context=context,
                results=reranked[:5],
            )
            generation_time = round((time() - t0) * 1000, 2)
            logger.info(f"生成完成: {len(response.answer)} chars, {generation_time}ms")
        except Exception as e:
            generation_time = round((time() - t0) * 1000, 2)
            return QAResponse(
                answer=f"[生成失败] {type(e).__name__}: {e}",
                sources=sources,
                retrieval_time=retrieval_time,
                generation_time=generation_time,
                total_time=round((time() - total_start) * 1000, 2),
            )

        total_time = round((time() - total_start) * 1000, 2)
        return QAResponse(
            answer=response.answer if hasattr(response, "answer") else str(response),
            sources=sources,
            retrieval_time=retrieval_time,
            generation_time=generation_time,
            total_time=total_time,
        )
