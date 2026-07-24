"""BGE-M3 API Embedding Provider — 通过 HTTP API 调用 Docker 上的 BGE-M3 服务。

使用 httpx 调用远程 Embedding API，无需本地加载模型文件。
"""

from typing import List
import httpx

from retrieval.embedding.base import BaseEmbedding
from core.exception import EmbeddingException
from core.logger import get_logger

logger = get_logger(__name__)


class BGEAPIEmbedding(BaseEmbedding):
    """BGE-M3 API Embedding 实现。

    通过 HTTP 调用 BGE-M3 Docker 服务的 /embed 端点。
    """

    def __init__(self, api_url: str = "http://localhost:8001/embed"):
        """初始化 BGE API Embedding。

        Args:
            api_url: BGE-M3 API 的 /embed 端点地址
        """
        self.api_url = api_url
        self._dimension = 1024  # BGE-M3 默认维度
        logger.info(f"BGE-M3 API Embedding 已配置: {api_url}")

    def embed_text(self, text: str) -> List[float]:
        """将单条文本转换为向量。"""
        if not text or not text.strip():
            raise EmbeddingException("输入文本为空")

        try:
            vectors = self._call_api([text])
            return vectors[0]
        except EmbeddingException:
            raise
        except Exception as e:
            raise EmbeddingException(f"Embedding API 调用失败: {str(e)}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """将多条文本转换为向量。"""
        if not texts:
            raise EmbeddingException("文本列表为空")

        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            raise EmbeddingException("所有输入文本均为空")

        try:
            return self._call_api(valid_texts)
        except EmbeddingException:
            raise
        except Exception as e:
            raise EmbeddingException(f"批量 Embedding API 调用失败: {str(e)}")

    def _call_api(self, texts: List[str]) -> List[List[float]]:
        """调用 BGE-M3 /embed API。

        API 格式:
            请求: POST /embed  {"texts": ["...", "..."]}
            响应: {"dimension": 1024, "count": N, "embeddings": [[...], [...]]}
        """
        try:
            with httpx.Client(timeout=30.0, trust_env=False) as client:
                resp = client.post(
                    self.api_url,
                    json={"texts": texts},
                    headers={"Content-Type": "application/json"}
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.ConnectError:
            raise EmbeddingException(f"无法连接到 BGE-M3 API: {self.api_url}")
        except httpx.TimeoutException:
            raise EmbeddingException(f"BGE-M3 API 请求超时: {self.api_url}")
        except httpx.HTTPStatusError as e:
            raise EmbeddingException(f"BGE-M3 API 返回错误 {e.response.status_code}: {e.response.text[:200]}")
        except Exception as e:
            raise EmbeddingException(f"BGE-M3 API 请求异常: {str(e)}")

        embeddings = data.get("embeddings")
        if embeddings is None:
            raise EmbeddingException(f"BGE-M3 API 返回数据缺少 'embeddings' 字段")

        # 更新实际维度
        if embeddings and len(embeddings) > 0:
            self._dimension = len(embeddings[0])

        return embeddings

    @property
    def dimension(self) -> int:
        """获取向量维度。"""
        return self._dimension
