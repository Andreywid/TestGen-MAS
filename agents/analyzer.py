from core.llm_client import call_llm, MODEL_STRONG

_SYSTEM = (
    "You are a senior Python test engineer. "
    "Your job is to analyze a Python function and produce a structured briefing "
    "that will be used by another agent to write pytest tests."
)

_USER_TEMPLATE = """\
Analyze the following Python function and return a structured briefing with these sections:

## Normal Cases
List the typical input/output pairs that should be tested.

## Edge Cases
List edge cases such as None, empty list, empty string, zero, negative numbers, very large numbers, type mismatches, etc.

## Branches
List all logical branches present in the code (if/else, try/except, loops, early returns).

Function source:
```python
{source}
```

Return only the briefing. No preamble, no explanation outside the sections."""


def analyze(source: str, model: str = MODEL_STRONG) -> str:
    """Retorna um briefing estruturado para o codigo-fonte fornecido."""
    user_prompt = _USER_TEMPLATE.format(source=source)
    return call_llm(_SYSTEM, user_prompt, model=model)
