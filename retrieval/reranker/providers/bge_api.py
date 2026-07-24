"""BGE-Rerank API Provider — 通过 HTTP API 调用 Docker 上的 BGE-Rerank 服务。

使用 httpx 调用远程 Rerank API，无需本地加载模型文件。
"""

from typing import List
import httpx

from retrieval.reranker.base import BaseReranker
from retrieval.retriever.model import RetrievalResult
from core.exception import RerankException
from core.logger import get_logger

logger = get_logger(__name__)


class BGEAPIReranker(BaseReranker):
    """BGE-Rerank API 实现。

    通过 HTTP 调用 BGE-Rerank Docker 服务的 /rerank 端点。
    """

    def __init__(self, api_url: str = "http://localhost:8002/rerank"):
        """初始化 BGE API Reranker。

        Args:
            api_url: BGE-Rerank API 的 /rerank 端点地址
        """
        self.api_url = api_url
        logger.info(f"BGE-Rerank API 已配置: {api_url}")

    def rerank(self, query: str, documents: List[RetrievalResult]) -> List[RetrievalResult]:
        """对文档列表进行重排序。"""
        if not query or not query.strip():
            raise RerankException("查询文本为空")

        if not documents:
            return []

        try:
            doc_texts = [doc.content for doc in documents]
            scores = self._call_api(query, doc_texts)

            # 将分数与原始文档关联并按分数降序排序
            scored = sorted(
                zip(documents, scores),
                key=lambda x: x[1],
                reverse=True,
            )

            result = []
            for doc, score in scored:
                result.append(RetrievalResult(
                    chunk_id=doc.chunk_id,
                    score=float(score),
                    content=doc.content,
                    metadata=doc.metadata,
                ))
            return result

        except RerankException:
            raise
        except Exception as e:
            raise RerankException(f"Rerank API 调用失败: {str(e)}")

    def _call_api(self, query: str, documents: List[str]) -> List[float]:
        """调用 BGE-Rerank /rerank API。

        API 格式（兼容两种常见响应）：
            请求: POST /rerank  {"query": "...", "documents": ["...", "..."]}
            响应A: {"scores": [0.95, 0.30, ...]}
            响应B: {"results": [{"index": 0, "relevance_score": 0.95}, ...]}
        """
        try:
            with httpx.Client(timeout=30.0, trust_env=False) as client:
                resp = client.post(
                    self.api_url,
                    json={"query": query, "documents": documents},
                    headers={"Content-Type": "application/json"},
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.ConnectError:
            raise RerankException(f"无法连接到 BGE-Rerank API: {self.api_url}")
        except httpx.TimeoutException:
            raise RerankException(f"BGE-Rerank API 请求超时: {self.api_url}")
        except httpx.HTTPStatusError as e:
            raise RerankException(
                f"BGE-Rerank API 返回错误 {e.response.status_code}: {e.response.text[:200]}"
            )
        except Exception as e:
            raise RerankException(f"BGE-Rerank API 请求异常: {str(e)}")

        # 兼容两种响应格式
        if "scores" in data:
            return data["scores"]
        if "results" in data:
            return [item.get("relevance_score", item.get("score", 0.0))
                    for item in data["results"]]

        raise RerankException(
            f"BGE-Rerank API 返回数据缺少 'scores' 或 'results' 字段: {list(data.keys())}"
        )
