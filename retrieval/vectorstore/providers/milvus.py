"""Milvus VectorStore Provider — 基于 Milvus 向量数据库的实现。

使用 pymilvus 库实现与 Milvus 的交互。
"""

from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4
import numpy as np

from retrieval.vectorstore.base import BaseVectorStore
from core.exception import VectorStoreException
from core.logger import get_logger
from core.config import get_config

logger = get_logger(__name__)


class MilvusVectorStore(BaseVectorStore):
    """Milvus 向量存储实现。"""

    def __init__(self, collection_name: str = "bestrag_chunks"):
        """初始化 Milvus 向量存储。

        Args:
            collection_name: 集合名称
        """
        try:
            from pymilvus import Collection, connections, utility, FieldSchema, CollectionSchema, DataType
        except ImportError:
            raise VectorStoreException(
                "pymilvus not installed. Please install it with: pip install pymilvus"
            )

        self.connections = connections
        self.Collection = Collection
        self.utility = utility
        self.FieldSchema = FieldSchema
        self.CollectionSchema = CollectionSchema
        self.DataType = DataType

        # 获取配置
        config = get_config().retrieval
        self.host = config.milvus_host
        self.port = config.milvus_port
        self.collection_name = f"{config.milvus_collection_prefix}_{collection_name}"

        # 记录向量维度（初始化后设置）
        self._dimension = config.embedding_dim

        # 连接到 Milvus
        try:
            self.connections.connect(alias="default", host=self.host, port=self.port)
            logger.info(f"Connected to Milvus: {self.host}:{self.port}")
        except Exception as e:
            raise VectorStoreException(f"Failed to connect to Milvus: {str(e)}")

        # 创建或连接到集合
        self._create_collection_if_not_exists()

    def _create_collection_if_not_exists(self):
        """创建集合（如果不存在）。"""
        if self.utility.has_collection(self.collection_name):
            # 如果集合已存在，获取其维度信息
            collection = self.Collection(self.collection_name)
            schema = collection.schema
            for field in schema.fields:
                if field.dtype == self.DataType.FLOAT_VECTOR:
                    self._dimension = field.params["dim"]
                    break
            logger.info(f"Using existing collection: {self.collection_name}")
        else:
            # 创建新的集合
            fields = [
                self.FieldSchema("id", self.DataType.VARCHAR, is_primary=True, max_length=65535),
                self.FieldSchema("vector", self.DataType.FLOAT_VECTOR, dim=self._dimension),
                self.FieldSchema("text", self.DataType.VARCHAR, max_length=65535),
                self.FieldSchema("metadata", self.DataType.JSON)
            ]

            schema = self.CollectionSchema(fields, f"BestRAG collection for {self.collection_name}")

            collection = self.Collection(self.collection_name, schema)

            # 创建索引
            index_params = {
                "index_type": "IVF_FLAT",
                "metric_type": "COSINE",
                "params": {"nlist": 128}
            }
            collection.create_index(field_name="vector", index_params=index_params)

            logger.info(f"Created collection: {self.collection_name}")

    def add(
        self,
        vectors: List[List[float]],
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """添加向量到存储。

        Args:
            vectors: 向量列表
            texts: 文本列表
            metadatas: 元数据列表
            ids: ID 列表，如果为 None 则自动生成

        Returns:
            添加成功的 ID 列表
        """
        if not vectors or not texts:
            raise VectorStoreException("Vectors and texts cannot be empty")

        if len(vectors) != len(texts):
            raise VectorStoreException("Vectors and texts length mismatch")

        # 准备数据
        if ids is None:
            ids = [str(uuid4()) for _ in range(len(vectors))]

        if metadatas is None:
            metadatas = [{} for _ in range(len(vectors))]

        # 确保向量是正确的维度
        for i, vec in enumerate(vectors):
            if len(vec) != self._dimension:
                raise VectorStoreException(f"Vector {i} has incorrect dimension: expected {self._dimension}, got {len(vec)}")

        # 准备插入的数据
        entities = [
            ids,
            vectors,
            texts,
            metadatas
        ]

        try:
            collection = self.Collection(self.collection_name)
            collection.load()  # 加载集合到内存

            # 插入数据
            insert_result = collection.insert(entities)

            # 刷新以确保数据可见
            collection.flush()

            logger.info(f"Inserted {len(ids)} vectors into collection {self.collection_name}")

            return ids
        except Exception as e:
            raise VectorStoreException(f"Failed to add vectors to Milvus: {str(e)}")

    def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, str, Dict[str, Any]]]:
        """搜索相似向量。

        Args:
            query_vector: 查询向量
            top_k: 返回结果数量
            filters: 过滤条件

        Returns:
            包含 (ID, 相似度分数, 文本, 元数据) 的元组列表
        """
        if len(query_vector) != self._dimension:
            raise VectorStoreException(f"Query vector has incorrect dimension: expected {self._dimension}, got {len(query_vector)}")

        try:
            collection = self.Collection(self.collection_name)
            collection.load()  # 加载集合到内存

            # 构建查询表达式
            expr = None
            if filters:
                # 转换过滤器为 Milvus 表达式
                expr_parts = []
                for key, value in filters.items():
                    if isinstance(value, str):
                        expr_parts.append(f'metadata["{key}"] == "{value}"')
                    elif isinstance(value, (int, float)):
                        expr_parts.append(f'metadata["{key}"] == {value}')
                    else:
                        expr_parts.append(f'metadata["{key}"] == "{str(value)}"')

                expr = " and ".join(expr_parts) if expr_parts else None

            # 执行搜索
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }

            results = collection.search(
                data=[query_vector],
                anns_field="vector",
                param=search_params,
                limit=top_k,
                expr=expr,
                output_fields=["text", "metadata"]
            )

            # 处理结果
            formatted_results = []
            for hits in results:
                for hit in hits:
                    formatted_results.append((
                        hit.id,
                        1 - hit.distance,  # 转换距离为相似度分数
                        hit.entity.text,
                        hit.entity.metadata
                    ))

            logger.info(f"Search completed, found {len(formatted_results)} results")

            return formatted_results
        except Exception as e:
            raise VectorStoreException(f"Failed to search vectors in Milvus: {str(e)}")

    def delete(self, ids: List[str]) -> bool:
        """删除向量。

        Args:
            ids: 要删除的 ID 列表

        Returns:
            删除是否成功
        """
        try:
            collection = self.Collection(self.collection_name)
            collection.load()  # 加载集合到内存

            # 删除数据
            delete_expr = f"id in [{', '.join([f'\"{id}\"' for id in ids])}]"
            delete_result = collection.delete(delete_expr)

            # 刷新以确保变更生效
            collection.flush()

            logger.info(f"Deleted {len(ids)} vectors from collection {self.collection_name}")

            return True
        except Exception as e:
            raise VectorStoreException(f"Failed to delete vectors from Milvus: {str(e)}")

    def get_dimension(self) -> int:
        """获取向量维度。"""
        return self._dimension

    def close(self) -> None:
        """关闭连接。"""
        try:
            self.connections.disconnect(alias="default")
            logger.info("Disconnected from Milvus")
        except Exception:
            # 忽略关闭连接时的错误
            pass