"""QA Scenario — 验证 RAG 问答全流程。

流程::

    用户问题 → QAService.ask() → 答案 + 来源

验证内容：
- Retrieval 返回结果
- Source 存在且非空
- Generation 返回回答
- 回答非空
"""

from time import time

from validation.model import ScenarioResult, CheckResult, ValidationStatus

_TEST_QUERY = "如何安装 BestRAG？"


def run_qa_scenario(qa_service=None) -> ScenarioResult:
    """执行 QA 问答场景验证。

    Args:
        qa_service: QAService 实例。

    Returns:
        ScenarioResult（含各步骤检查项）。
    """
    name = "qa"
    checks: list[CheckResult] = []
    start = time()

    if qa_service is None:
        return ScenarioResult(
            name=name,
            status=ValidationStatus.SKIP,
            checks=[CheckResult(name=name, status=ValidationStatus.SKIP, message="QAService 未注入")],
        )

    try:
        from features.model import QARequest

        # ── Step 1: 执行问答 ──
        t0 = time()
        req = QARequest(query=_TEST_QUERY, top_k=5)
        response = qa_service.ask(req)
        qa_latency = round((time() - t0) * 1000, 2)

        # ── Step 2: 检查检索结果 ──
        sources = response.sources or []
        if len(sources) == 0:
            checks.append(CheckResult(
                name="retrieval",
                status=ValidationStatus.FAIL,
                message="检索返回 0 条结果（知识库可能为空）",
                latency=response.retrieval_time,
            ))
        else:
            checks.append(CheckResult(
                name="retrieval",
                status=ValidationStatus.PASS,
                message=f"检索返回 {len(sources)} 条结果",
                latency=response.retrieval_time,
                details={"source_count": len(sources), "top_score": sources[0].get("score")},
            ))

        # ── Step 3: 检查 Source 完整性 ──
        valid_sources = [s for s in sources if s.get("content")]
        if len(sources) > 0 and len(valid_sources) == 0:
            checks.append(CheckResult(
                name="sources",
                status=ValidationStatus.FAIL,
                message="Source 内容全部为空",
            ))
        else:
            checks.append(CheckResult(
                name="sources",
                status=ValidationStatus.PASS if len(valid_sources) > 0 else ValidationStatus.SKIP,
                message=f"有效 Source: {len(valid_sources)}/{len(sources)}",
                details={"valid_count": len(valid_sources)},
            ))

        # ── Step 4: 检查回答 ──
        answer = response.answer or ""
        if not answer.strip():
            checks.append(CheckResult(
                name="generation",
                status=ValidationStatus.FAIL,
                message="回答为空",
                latency=response.generation_time,
            ))
        elif answer.startswith("[") and "错误" in answer:
            checks.append(CheckResult(
                name="generation",
                status=ValidationStatus.FAIL,
                message=f"生成异常: {answer[:100]}",
                latency=response.generation_time,
            ))
        else:
            checks.append(CheckResult(
                name="generation",
                status=ValidationStatus.PASS,
                message=f"回答正常: {len(answer)} chars",
                latency=response.generation_time,
                details={"answer_preview": answer[:200], "answer_length": len(answer)},
            ))

        return _build_result(name, checks, start, response.retrieval_time, response.generation_time, response.total_time)

    except Exception as e:
        checks.append(CheckResult(
            name=name,
            status=ValidationStatus.FAIL,
            message=f"场景异常: {type(e).__name__}: {e}",
        ))
        return _build_result(name, checks, start)


def _build_result(
    name: str, checks: list[CheckResult], start: float,
    retrieval_time: float = 0, generation_time: float = 0, total_time: float = 0,
) -> ScenarioResult:
    duration = round(time() - start, 3)
    fail_count = sum(1 for c in checks if c.status == ValidationStatus.FAIL)
    return ScenarioResult(
        name=name,
        status=ValidationStatus.FAIL if fail_count > 0 else ValidationStatus.PASS,
        duration=duration,
        checks=checks,
        details={
            "retrieval_time_ms": retrieval_time,
            "generation_time_ms": generation_time,
            "total_time_ms": total_time,
        },
    )
