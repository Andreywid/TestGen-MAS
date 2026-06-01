from core.llm_client import call_llm, MODEL_STRONG
from core.models import ExecutionResult, ReviewReport

_SYSTEM = (
    "You are a senior Python test engineer performing a code review. "
    "Your job is to identify specific problems in failing or low-quality pytest tests."
)

_USER_TEMPLATE = """\
Review the pytest test file below against the original function.

For each failing or problematic test, identify exactly what is wrong. Focus on:
- Incorrect assertions (wrong expected value, wrong comparison)
- Missing or wrong imports
- Tests that do not actually call the function under test
- Trivial tests that always pass regardless of the implementation
- Tests that fail due to incorrect assumptions about the function's behavior

Original function:
```python
{source}
```

Test file:
```python
{test_code}
```

Execution results:
{execution_summary}

Return a structured report. For each problematic test, output a block like:

TEST: <test_function_name>
PROBLEM: <one-sentence diagnosis>

Only include tests that have a real problem. Do not include passing tests that are correct.
Output only the structured report. No preamble, no markdown fences."""


def _format_execution_summary(exec_result: ExecutionResult) -> str:
    lines = []
    for t in exec_result.test_results:
        line = f"- {t.name}: {t.status.value}"
        if t.error_message:
            msg = t.error_message[:300].replace("\n", " ")
            line += f" | {msg}"
        lines.append(line)
    lines.append(f"Coverage: {exec_result.coverage_percent:.1f}%")
    return "\n".join(lines)


def review(source: str, test_code: str, exec_result: ExecutionResult, model: str = MODEL_STRONG) -> ReviewReport:
    """Return a ReviewReport mapping test names to problem diagnoses."""
    summary = _format_execution_summary(exec_result)
    user_prompt = _USER_TEMPLATE.format(
        source=source,
        test_code=test_code,
        execution_summary=summary,
    )

    raw = call_llm(_SYSTEM, user_prompt, model=model)

    diagnostics: dict[str, str] = {}
    current_test: str | None = None

    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("TEST:"):
            current_test = line[len("TEST:"):].strip()
        elif line.startswith("PROBLEM:") and current_test:
            diagnostics[current_test] = line[len("PROBLEM:"):].strip()
            current_test = None

    return ReviewReport(diagnostics=diagnostics)
