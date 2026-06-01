from dataclasses import dataclass, field
from enum import Enum


class TestStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


@dataclass
class TestResult:
    name: str
    status: TestStatus
    error_message: str | None = None
    coverage_contributed: float = 0.0


@dataclass
class ReviewReport:
    diagnostics: dict[str, str] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    test_results: list[TestResult]
    coverage_percent: float
    raw_output: str

    @property
    def passing(self) -> list[TestResult]:
        return [t for t in self.test_results if t.status == TestStatus.PASSED]

    @property
    def failing(self) -> list[TestResult]:
        return [t for t in self.test_results if t.status != TestStatus.PASSED]


@dataclass
class PipelineOutput:
    mode: str  # "single_agent" ou "multi_agent"
    function_name: str
    approved_tests: list[TestResult]
    initial_coverage: float
    final_coverage: float
    refinement_iterations: int
    llm_calls: int
    raw_test_code: str
