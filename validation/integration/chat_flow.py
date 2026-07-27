"""Chat Flow — Chat 验证流程 + 系统状态检查。

流程::

    User Query → Retrieval → Generation → ChatResult

同时提供系统状态快照。
"""

from time import time
from typing import Optional

from validation.model import ChatResult, StatusResult, ValidationStatus


def run_chat_flow(
    query: str,
    retrieval_service=None,
    generation_service=None,
    embedding_service=None,
    vector_store_service=None,
    doc_service=None,
    processor_service=None,
    use_test_data: bool = False,
) -> ChatResult:
    """执行 Chat 验证流程。

    流程：
        1. 如果 use_test_data=True，自动生成测试文档并索引
        2. 执行检索
        3. 执行生成
        4. 返回 ChatResult

    Args:
        query:                 用户问题。
        retrieval_service:     RetrievalService 实例。
        generation_service:    GenerationService 实例。
        embedding_service:     EmbeddingService 实例。
        vector_store_service:  VectorStoreService 实例。
        doc_service:           DocumentService 实例（use_test_data 时必需）。
        processor_service:     ProcessorService 实例（use_test_data 时必需）。
        use_test_data:         是否自动生成测试数据。

    Returns:
        ChatResult。
    """
    result = ChatResult()
    total_start = time()
    context: str = ""

    # ── Step 0: 准备测试数据 ──
    if use_test_data:
        try:
            _prepare_test_data(
                doc_service=doc_service,
                processor_service=processor_service,
                embedding_service=embedding_service,
                vector_store_service=vector_store_service,
            )
        except Exception as e:
            result.metadata["test_data_error"] = str(e)

    # ── Step 1: Retrieval ──
    if retrieval_service is not None:
        t0 = time()
        try:
            results = retrieval_service.retrieve(query, top_k=5)
            result.retrieval_time = round((time() - t0) * 1000, 2)
            result.sources = [
                {
                    "chunk_id": r.chunk_id,
                    "score": r.score,
                    "content": r.content[:200],
                    "metadata": r.metadata,
                }
                for r in results
            ]
            # 构建 Context 供 Generation 使用
            context = "\n".join(r.content for r in results)
            result.metadata["retrieval_count"] = len(results)
        except Exception as e:
            result.retrieval_time = round((time() - t0) * 1000, 2)
            result.metadata["retrieval_error"] = str(e)
    else:
        result.metadata["retrieval"] = "RetrievalService 未注入"

    # ── Step 2: Generation ──
    if generation_service is not None:
        t0 = time()
        try:
            response = generation_service.generate(query=query, context=context)
            result.generation_time = round((time() - t0) * 1000, 2)
            result.answer = response.answer
            result.metadata["model"] = response.model
        except Exception as e:
            result.generation_time = round((time() - t0) * 1000, 2)
            result.answer = f"[Generation 失败] {e}"
            result.metadata["generation_error"] = str(e)
    else:
        result.answer = "[GenerationService 未注入]"

    result.total_time = round((time() - total_start) * 1000, 2)
    return result


def _prepare_test_data(
    doc_service=None,
    processor_service=None,
    embedding_service=None,
    vector_store_service=None,
) -> None:
    """生成测试文档并索引到向量库。

    使用固定的测试内容，确保 Chat API 自包含。
    """
    import tempfile
    from pathlib import Path

    test_content = (
        "# BestRAG 知识库\n\n"
        "## 简介\n"
        "BestRAG 是一个企业级 RAG 框架，支持多格式文档处理。\n\n"
        "## 部署\n"
        "安装 Python 3.10+，执行 uv sync 安装依赖。\n"
        "使用 uvicorn main:app --reload 启动服务。\n\n"
        "## 配置\n"
        "需要配置 Milvus 连接和 LLM API Key。\n"
    )

    # 写入临时文件
    f = tempfile.NamedTemporaryFile(suffix=".md", mode="w", encoding="utf-8", delete=False)
    f.write(test_content)
    f.close()
    test_path = f.name

    try:
        # Document parsing
        if doc_service is None:
            raise RuntimeError("DocumentService 未注入")
        doc = doc_service.create_document(test_path)

        # Processor
        if processor_service is not None:
            processed = processor_service.process(doc, "recursive")
            chunks = processed.chunks if hasattr(processed, "chunks") else []
            chunk_texts = [c.content if hasattr(c, "content") else str(c) for c in chunks]
        else:
            chunk_texts = [doc.content]

        # Embedding + Indexing
        if embedding_service is not None and vector_store_service is not None:
            embeddings = embedding_service.embed_documents(chunk_texts)
            vectors = [e.vector for e in embeddings]
            vector_store_service.add_texts(chunk_texts, vectors)
    finally:
        Path(test_path).unlink(missing_ok=True)


def get_status(
    embedding_service=None,
    vector_store_service=None,
    retrieval_service=None,
    rerank_service=None,
    generation_service=None,
) -> StatusResult:
    """获取系统各组件状态快照。

    检测各服务的可用性并返回状态。
    """
    import os

    result = StatusResult()
    details: dict = {}

    # ── Core ──
    core_ok = True

    # Embedding
    if embedding_service is not None:
        try:
            emb = embedding_service.embed_text("test")
            if emb and emb.vector:
                details["embedding"] = {"status": "ok", "dim": len(emb.vector)}
            else:
                details["embedding"] = {"status": "error", "message": "返回空向量"}
                core_ok = False
        except Exception as e:
            details["embedding"] = {"status": "error", "message": str(e)}
            core_ok = False
    else:
        details["embedding"] = {"status": "unknown"}

    # VectorStore
    if vector_store_service is not None:
        try:
            # 尝试获取 collection 信息
            info = vector_store_service.collection_info() if hasattr(vector_store_service, "collection_info") else None
            details["vectorstore"] = {"status": "ok", "info": str(info) if info else "connected"}
        except Exception as e:
            details["vectorstore"] = {"status": "error", "message": str(e)}
            core_ok = False
    else:
        details["vectorstore"] = {"status": "unknown"}

    result.core = "ok" if core_ok else "error"

    # ── Retrieval ──
    retrieval_ok = True
    if retrieval_service is not None:
        details["retrieval"] = {"status": "ok", "message": "RetrievalService 可用"}
    else:
        details["retrieval"] = {"status": "unknown"}
        retrieval_ok = False

    if rerank_service is not None:
        details["reranker"] = {"status": "ok", "message": "RerankService 可用"}
    else:
        details["reranker"] = {"status": "unknown"}

    result.retrieval = "ok" if retrieval_ok else "unknown"

    # ── Generation ──
    gen_ok = True
    if generation_service is not None:
        details["generation"] = {"status": "ok", "message": "GenerationService 可用"}
        # 检查 LLM 配置
        from core.config import get_config
        cfg = get_config().generation
        details["llm"] = {
            "status": "ok" if cfg.api_key or os.environ.get("BESTRAG_LLM_API_KEY") else "no_key",
            "model": cfg.model_name,
            "base_url": cfg.base_url,
        }
    else:
        details["generation"] = {"status": "unknown"}
        gen_ok = False

    result.generation = "ok" if gen_ok else "unknown"
    result.details = details

    return result
