from core.llm_client import call_llm, MODEL_FAST

_SYSTEM = (
    "You are a senior Python test engineer. "
    "Your job is to write a complete, runnable pytest test file for a given function."
)

_IMPORT_RULE = (
    "- The first two lines of the file MUST be:\n"
    "  import pytest\n"
    "  from {module} import {func}"
)

_COMMON_RULES = """\
- Use real assertions (assert statements with concrete expected values).
- Do NOT use mocks unless the function itself performs I/O or side effects.
- Do NOT redefine the function under test in the test file.
- Name each test function descriptively (e.g. test_empty_list, test_negative_number).
- Output ONLY the Python source code of the test file. No explanation, no markdown fences."""

_USER_TEMPLATE = """\
Write a pytest test file for the function below.

Rules:
{import_rule}
{common_rules}
- Cover every case listed in the briefing.

Function source:
```python
{source}
```

Test briefing:
{briefing}
"""

_USER_TEMPLATE_NO_BRIEFING = """\
Write a pytest test file for the function below.

Rules:
{import_rule}
{common_rules}
- Cover normal cases, edge cases (None, empty inputs, negative numbers, large inputs), and all logical branches.

Function source:
```python
{source}
```
"""


def generate(source: str, function_name: str, briefing: str | None = None, model: str = MODEL_FAST) -> str:
    """Return the content of a pytest test file for the given function."""
    import_rule = _IMPORT_RULE.format(module=function_name, func=function_name)

    if briefing:
        user_prompt = _USER_TEMPLATE.format(
            import_rule=import_rule,
            common_rules=_COMMON_RULES,
            source=source,
            briefing=briefing,
        )
    else:
        user_prompt = _USER_TEMPLATE_NO_BRIEFING.format(
            import_rule=import_rule,
            common_rules=_COMMON_RULES,
            source=source,
        )

    return call_llm(_SYSTEM, user_prompt, model=model)
