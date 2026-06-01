from agents import analyzer, executor, generator, refiner, reviewer, validator
from core import llm_client
from core.llm_client import MODEL_FAST, MODEL_STRONG
from core.models import PipelineOutput

_MAX_REFINE_ITERATIONS = 3


def _function_name_from_source(source: str) -> str:
    for line in source.splitlines():
        line = line.strip()
        if line.startswith("def "):
            return line[4:].split("(")[0].strip()
    return "function"


def run_single_agent(source: str, model: str | None = None) -> PipelineOutput:
    """Modo baseline: Generator -> Executor -> Validator."""
    func_name = _function_name_from_source(source)
    llm_client.reset_call_count()

    gen_model = model or MODEL_FAST
    test_code = generator.generate(source, func_name, briefing=None, model=gen_model)
    exec_result = executor.execute(test_code, func_name, source=source)
    approved, final_cov = validator.validate(exec_result, baseline_coverage=0.0)

    return PipelineOutput(
        mode="single_agent",
        function_name=func_name,
        approved_tests=approved,
        initial_coverage=exec_result.coverage_percent,
        final_coverage=final_cov,
        refinement_iterations=0,
        llm_calls=llm_client.get_call_count(),
        raw_test_code=test_code,
    )


def run_multi_agent(source: str, model: str | None = None) -> PipelineOutput:
    """Pipeline completo: Analyzer -> Generator -> Executor -> [Reviewer -> Refiner] x3 -> Validator."""
    func_name = _function_name_from_source(source)
    llm_client.reset_call_count()

    # se model esta fixado, todos os agentes usam o mesmo; caso contrario, mixed (padrão)
    strong = model or MODEL_STRONG
    fast = model or MODEL_FAST

    briefing = analyzer.analyze(source, model=strong)
    test_code = generator.generate(source, func_name, briefing=briefing, model=fast)
    first_exec = executor.execute(test_code, func_name, source=source)

    # se o briefing causou geracao quebrada, usa generator sem briefing
    if len(first_exec.test_results) == 0 or first_exec.coverage_percent == 0.0:
        test_code = generator.generate(source, func_name, briefing=None, model=fast)
        first_exec = executor.execute(test_code, func_name, source=source)

    best_code = test_code
    best_exec = first_exec
    best_pass = len(first_exec.passing)

    current_code = test_code
    exec_result = first_exec
    iterations_used = 0

    for _ in range(_MAX_REFINE_ITERATIONS):
        if not exec_result.failing:
            break

        review_report = reviewer.review(source, current_code, exec_result, model=strong)
        failing_names = [t.name for t in exec_result.failing]
        current_code = refiner.refine(source, current_code, review_report, failing_names, model=fast)

        exec_result = executor.execute(current_code, func_name, source=source)

        if len(exec_result.passing) > best_pass:
            best_code = current_code
            best_exec = exec_result
            best_pass = len(exec_result.passing)
            iterations_used += 1
        else:
            # sem melhora: repetir com as mesmas entradas nao vai ajudar
            current_code = best_code
            exec_result = best_exec
            break

    approved, final_cov = validator.validate(best_exec, baseline_coverage=0.0)

    return PipelineOutput(
        mode="multi_agent",
        function_name=func_name,
        approved_tests=approved,
        initial_coverage=first_exec.coverage_percent,
        final_coverage=final_cov,
        refinement_iterations=iterations_used,
        llm_calls=llm_client.get_call_count(),
        raw_test_code=best_code,
    )


def run(source: str, mode: str, model: str | None = None) -> PipelineOutput:
    if mode == "single_agent":
        return run_single_agent(source, model=model)
    if mode == "multi_agent":
        return run_multi_agent(source, model=model)
    raise ValueError(f"Unknown mode: {mode!r}. Use 'single_agent' or 'multi_agent'.")
