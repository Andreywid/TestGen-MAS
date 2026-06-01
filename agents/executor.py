import re
import subprocess
import sys
import tempfile
from pathlib import Path

from core.models import ExecutionResult, TestResult, TestStatus

_TIMEOUT = 30  # segundos

# formato verboso: "test_foo.py::test_bar PASSED [ 16%]"
# formato sumario:  "FAILED test_foo.py::test_bar - motivo"
_VERBOSE_LINE = re.compile(r"([\w/\\.:]+::[\w\[\]-]+)\s+(PASSED|FAILED|ERROR)")
_SUMMARY_LINE = re.compile(r"^(FAILED|ERROR)\s+([\w/\\.:]+::[\w\[\]-]+)", re.MULTILINE)


def _parse_pytest_output(output: str) -> list[TestResult]:
    status_map = {
        "PASSED": TestStatus.PASSED,
        "FAILED": TestStatus.FAILED,
        "ERROR": TestStatus.ERROR,
    }
    seen: dict[str, TestResult] = {}

    # verboso cobre PASSED, que o sumario omite
    for match in _VERBOSE_LINE.finditer(output):
        name, raw_status = match.group(1), match.group(2)
        seen[name] = TestResult(name=name, status=status_map[raw_status])

    # sumario cobre FAILED/ERROR que o verboso perde
    for match in _SUMMARY_LINE.finditer(output):
        raw_status, name = match.group(1), match.group(2)
        if name not in seen:
            seen[name] = TestResult(name=name, status=status_map[raw_status])

    return list(seen.values())


def _parse_coverage(output: str) -> float:
    # pytest-cov imprime: TOTAL   150   12   92%
    match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
    if match:
        return float(match.group(1))
    # fallback para relatorio de arquivo unico: "add.py   5   0   100%"
    match = re.search(r"\w+\.py\s+\d+\s+\d+\s+(\d+)%", output)
    if match:
        return float(match.group(1))
    return 0.0


def _attach_error_messages(results: list[TestResult], output: str) -> None:
    for result in results:
        if result.status == TestStatus.PASSED:
            continue
        short_name = result.name.split("::")[-1]
        pattern = re.compile(
            rf"FAILED {re.escape(result.name)}[^\n]*\n(.*?)(?=\n(?:PASSED|FAILED|ERROR|={5})|$)",
            re.DOTALL,
        )
        match = pattern.search(output)
        if match:
            result.error_message = match.group(1).strip()
        else:
            result.error_message = f"See full output for {short_name}"


def _strip_markdown_fences(code: str) -> str:
    code = code.strip()
    if code.startswith("```"):
        code = re.sub(r"^```[^\n]*\n?", "", code)
        code = re.sub(r"\n?```$", "", code)
    return code.strip()


def execute(test_code: str, function_name: str, source: str | None = None) -> ExecutionResult:
    """Salva fonte e testes em diretorio temporario, roda pytest com cobertura e retorna resultados."""
    test_code = _strip_markdown_fences(test_code)

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)

        if source:
            (base / f"{function_name}.py").write_text(source, encoding="utf-8")

        (base / f"test_{function_name}.py").write_text(test_code, encoding="utf-8")

        # nome do modulo para o pytest-cov medir a cobertura do arquivo correto
        cov_target = function_name if source else "."

        cmd = [
            sys.executable, "-m", "pytest",
            f"test_{function_name}.py",
            "--tb=short",
            "-v",
            f"--cov={cov_target}",
            "--cov-report=term-missing",
            "--no-header",
        ]

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT,
            cwd=str(base),
        )

        combined = proc.stdout + proc.stderr
        test_results = _parse_pytest_output(combined)
        _attach_error_messages(test_results, combined)
        coverage = _parse_coverage(combined)

        return ExecutionResult(
            test_results=test_results,
            coverage_percent=coverage,
            raw_output=combined,
        )
