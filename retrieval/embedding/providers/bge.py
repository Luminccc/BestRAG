"""BGE Embedding Provider — 基于 BAAI/bge-base-en-v1.5 模型的 Embedding 实现。

使用 sentence-transformers 库实现。
"""

from typing import List
import numpy as np

from retrieval.embedding.base import BaseEmbedding
from core.exception import EmbeddingException
from core.logger import get_logger

logger = get_logger(__name__)


class BGEEmbedding(BaseEmbedding):
    """BGE Embedding 实现。"""

    def __init__(self, model_name: str = "BAAI/bge-base-en-v1.5"):
        """初始化 BGE Embedding。

        Args:
            model_name: 模型名称
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            logger.info(f"BGE Embedding model loaded: {model_name}")
        except ImportError:
            raise EmbeddingException(
                "sentence-transformers not installed. Please install it with: pip install sentence-transformers"
            )
        except Exception as e:
            raise EmbeddingException(f"Failed to load BGE model: {str(e)}")

    def embed_text(self, text: str) -> List[float]:
        """将单条文本转换为向量。

        Args:
            text: 输入文本

        Returns:
            文本的向量表示

        Raises:
            EmbeddingException: Embedding 过程中出现错误
        """
        if not text or not text.strip():
            raise EmbeddingException("Input text is empty")

        try:
            # 使用模型进行编码
            vector = self.model.encode(text, normalize_embeddings=True)
            # 转换为 Python 列表
            return vector.tolist()
        except Exception as e:
            raise EmbeddingException(f"Failed to embed text: {str(e)}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """将多条文本转换为向量。

        Args:
            texts: 输入文本列表

        Returns:
            文本的向量表示列表

        Raises:
            EmbeddingException: Embedding 过程中出现错误
        """
        if not texts:
            raise EmbeddingException("Input texts list is empty")

        # 过滤空文本
        valid_texts = [text for text in texts if text and text.strip()]
        if not valid_texts:
            raise EmbeddingException("All input texts are empty")

        try:
            # 批量编码
            vectors = self.model.encode(valid_texts, normalize_embeddings=True)
            # 转换为 Python 列表
            return vectors.tolist()
        except Exception as e:
            raise EmbeddingException(f"Failed to embed documents: {str(e)}")

    @property
    def dimension(self) -> int:
        """获取向量维度。"""
        # 使用模型配置中的维度信息
        try:
            return self.model.get_sentence_embedding_dimension()
        except AttributeError:
            # 某些模型版本可能没有此方法，使用默认值
            # 可以通过编码一个样本获取维度
            sample_embedding = self.model.encode(["test"])
            return len(sample_embedding[0]) if len(sample_embedding) > 0 else 384