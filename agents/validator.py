from core.models import ExecutionResult, TestResult, TestStatus


def validate(
    exec_result: ExecutionResult,
    baseline_coverage: float,
) -> tuple[list[TestResult], float]:
    """Filtra testes aprovados e retorna (aprovados, cobertura_final)."""
    approved: list[TestResult] = []

    for test in exec_result.test_results:
        if test.status == TestStatus.ERROR:
            msg = (test.error_message or "").lower()
            if "importerror" in msg or "syntaxerror" in msg or "modulenot" in msg:
                continue

        if test.status != TestStatus.PASSED:
            continue

        approved.append(test)

    final_coverage = exec_result.coverage_percent
    if final_coverage <= baseline_coverage:
        return [], final_coverage

    return approved, final_coverage
