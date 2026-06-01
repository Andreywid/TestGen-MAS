import ast
import re

from core.llm_client import call_llm, MODEL_FAST
from core.models import ReviewReport

_SYSTEM = (
    "You are a senior Python test engineer. "
    "Your job is to fix a single broken pytest test function given a diagnosis of the problem."
)

_USER_TEMPLATE = """\
Fix ONLY the failing test function shown below. Do not change anything else.

Original function under test:
```python
{source}
```

Current (broken) test function:
```python
{test_function}
```

Diagnosis:
{diagnosis}

Rules:
- Return ONLY the corrected `def test_...` function body. Nothing else.
- Keep the exact same function name.
- Do not include imports or any code outside the function.
- Use real assertions with concrete expected values.
- Assume `import pytest` and `from {module} import {func}` are already at the top of the file."""

_FULL_FILE_MARKER = re.compile(r"^(import |from )", re.MULTILINE)


def _extract_func_name_from_source(source: str) -> str:
    for line in source.splitlines():
        line = line.strip()
        if line.startswith("def "):
            return line[4:].split("(")[0].strip()
    return "function"


def _strip_fences(code: str) -> str:
    code = code.strip()
    if code.startswith("```"):
        code = re.sub(r"^```[^\n]*\n?", "", code)
        code = re.sub(r"\n?```\s*$", "", code)
    return code.strip()


def _extract_function(name: str, test_code: str) -> str | None:
    pattern = re.compile(
        rf"^(def {re.escape(name)}\b.*?(?=\ndef |\Z))",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(test_code)
    return match.group(0).rstrip() if match else None


def _replace_function(name: str, test_code: str, new_body: str) -> str:
    pattern = re.compile(
        rf"^def {re.escape(name)}\b.*?(?=\ndef |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    replacement = new_body.rstrip() + "\n"
    return pattern.sub(lambda _: replacement, test_code, count=1)


def _is_valid_python(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def _looks_like_full_file(code: str) -> bool:
    return bool(_FULL_FILE_MARKER.search(code)) and "def test_" in code


def refine(
    source: str,
    test_code: str,
    review_report: ReviewReport,
    failing_test_names: list[str],
    model: str = MODEL_FAST,
) -> str:
    """Attempt one LLM fix per failing test. Returns the updated test file."""
    current_code = test_code
    func_name = _extract_func_name_from_source(source)

    for test_name in failing_test_names:
        short_name = test_name.split("::")[-1]
        diagnosis = (
            review_report.diagnostics.get(short_name)
            or review_report.diagnostics.get(test_name)
            or "Unknown failure: rewrite the test with a correct assertion."
        )

        test_fn = _extract_function(short_name, current_code)
        if test_fn is None:
            continue

        user_prompt = _USER_TEMPLATE.format(
            source=source,
            test_function=test_fn,
            diagnosis=diagnosis,
            module=func_name,
            func=func_name,
        )
        fixed = _strip_fences(call_llm(_SYSTEM, user_prompt, model=model))

        if _looks_like_full_file(fixed):
            extracted = _extract_function(short_name, fixed)
            if extracted:
                fixed = extracted

        if fixed.startswith("def "):
            candidate = _replace_function(short_name, current_code, fixed)
            if _is_valid_python(candidate):
                current_code = candidate

    return current_code
