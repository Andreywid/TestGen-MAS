import dataclasses
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from core.llm_client import MODEL_FAST, MODEL_STRONG
from core.pipeline import run
from data.humaneval_samples.samples import SAMPLES

_RESULTS_DIR = Path(__file__).parent / "results"

# codigos de cor e estilo ANSI
_G = "\033[92m"   # verde
_R = "\033[91m"   # vermelho
_Y = "\033[93m"   # amarelo
_C = "\033[96m"   # ciano
_B = "\033[1m"    # negrito
_D = "\033[2m"    # esmaecido
_X = "\033[0m"    # reset

_W = 64


def _hline(char="─"):
    return char * _W


def _banner() -> None:
    title = "TestGen-MAS  ·  Multi-Agent Unit Test Generator"
    pad_l = (_W - len(title)) // 2
    pad_r = _W - len(title) - pad_l
    print(f"\n{_B}╔{'═' * _W}╗")
    print(f"║{' ' * pad_l}{title}{' ' * pad_r}║")
    print(f"╚{'═' * _W}╝{_X}")


def _section(title: str) -> None:
    label = f" {title} "
    filler = _W - len(label)
    left = filler // 2
    right = filler - left
    print(f"\n{_B}{_C}{'━' * left}{label}{'━' * right}{_X}")


def _cov_color(cov: float) -> str:
    if cov >= 90:
        return _G
    if cov >= 60:
        return _Y
    return _R


def _output_path(label: str) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return _RESULTS_DIR / f"{label}_{ts}.json"


def run_experiment(modes: list[str], samples: list[dict], model: str | None, model_label: str) -> None:
    _RESULTS_DIR.mkdir(exist_ok=True)

    _banner()
    if model_label == "mixed":
        print(f"\n  {_D}Model (analyze/review) : {MODEL_STRONG}{_X}")
        print(f"  {_D}Model (generate/refine): {MODEL_FAST}{_X}")
    else:
        print(f"\n  {_D}Model  : {model} ({model_label}){_X}")
    print(f"  {_D}Modes  : {', '.join(modes)}{_X}")
    print(f"  {_D}Samples: {len(samples)} HumanEval functions{_X}")

    all_records: dict[str, list[dict]] = {}

    for mode in modes:
        _section(mode.upper().replace("_", " "))
        records: list[dict] = []

        for sample in samples:
            func_name = sample["name"]
            print(f"\n  {_D}▶{_X} {_B}{func_name}{_X}", flush=True)

            t0 = time.time()
            try:
                output = run(sample["source"], mode=mode, model=model)
                elapsed = time.time() - t0
                n = len(output.approved_tests)
                cov = output.final_coverage

                tc = _G if n > 0 else _R
                cc = _cov_color(cov)
                iter_label = f"{output.refinement_iterations}× refined" if output.refinement_iterations else "no refinement"

                print(
                    f"    {tc}{_B}{n} tests approved{_X}"
                    f"  {cc}{cov:.1f}% coverage{_X}"
                    f"  {_D}{iter_label}  {output.llm_calls} calls  {elapsed:.1f}s{_X}"
                )
                for t in output.approved_tests:
                    short = t.name.split("::")[-1]
                    print(f"    {_G}✓{_X} {_D}{short}{_X}")

                record = {
                    "task_id": sample["task_id"],
                    "function_name": func_name,
                    "mode": mode,
                    "model_config": model_label,
                    "approved_tests_count": n,
                    "initial_coverage": output.initial_coverage,
                    "final_coverage": cov,
                    "refinement_iterations": output.refinement_iterations,
                    "llm_calls": output.llm_calls,
                    "elapsed_seconds": round(elapsed, 2),
                    "approved_tests": [dataclasses.asdict(t) for t in output.approved_tests],
                }

            except Exception as exc:
                elapsed = time.time() - t0
                print(f"    {_R}✗ FAILED{_X}  {_D}{exc}{_X}")
                record = {
                    "task_id": sample["task_id"],
                    "function_name": func_name,
                    "mode": mode,
                    "error": str(exc),
                    "elapsed_seconds": round(elapsed, 2),
                }

            records.append(record)

        all_records[mode] = records
        path = _output_path(mode)
        path.write_text(json.dumps(records, indent=2), encoding="utf-8")
        print(f"\n  {_D}→ Saved: {path}{_X}")

    if len(all_records) >= 2:
        _print_comparison_table(all_records)
    else:
        _print_single_mode_summary(all_records)

    summary_path = _output_path("summary")
    summary_path.write_text(json.dumps(all_records, indent=2), encoding="utf-8")
    print(f"  {_D}→ Summary: {summary_path}{_X}\n")


def _print_comparison_table(all_records: dict[str, list[dict]]) -> None:
    modes = list(all_records.keys())
    col = 16

    print(f"\n{_B}  {_hline()}{_X}")
    print(f"{_B}  Comparison Summary{_X}")
    print(f"  {_hline()}")
    header = f"  {'Function':<30}"
    for m in modes:
        label = m.replace("_", " ")
        header += f"  {label:>{col}}"
    print(f"{_B}{header}{_X}")
    print(f"  {_hline()}")

    all_funcs: list[str] = []
    for records in all_records.values():
        for r in records:
            if r["function_name"] not in all_funcs:
                all_funcs.append(r["function_name"])

    totals = {m: {"tests": 0, "ok": 0, "calls": 0, "secs": 0.0} for m in modes}

    for fn in all_funcs:
        row = f"  {fn:<30}"
        for m in modes:
            rec = next((r for r in all_records[m] if r["function_name"] == fn), None)
            if rec is None:
                row += f"  {'n/a':>{col}}"
            elif "error" in rec:
                row += f"  {_R}{'ERROR':>{col}}{_X}"
            else:
                n = rec["approved_tests_count"]
                cov = rec["final_coverage"]
                tc = _G if n > 0 else _R
                cc = _cov_color(cov)
                cell = f"{tc}{n}t{_X} {cc}{cov:.1f}%{_X}"
                # celula tem codigos ANSI, padding feito manualmente
                visible = f"{n}t {cov:.1f}%"
                pad = col - len(visible)
                row += f"  {' ' * pad}{cell}"
                totals[m]["tests"] += n
                totals[m]["calls"] += rec.get("llm_calls", 0)
                totals[m]["secs"] += rec.get("elapsed_seconds", 0.0)
                if n > 0:
                    totals[m]["ok"] += 1
        print(row)

    print(f"  {_hline()}")
    total_row = f"  {'TOTAL tests':<30}"
    for m in modes:
        t = totals[m]
        cell_str = f"{t['tests']}t  {t['ok']}/{len(all_funcs)} fns"
        total_row += f"  {cell_str:>{col}}"
    print(f"{_B}{total_row}{_X}")

    cost_row = f"  {'TOTAL cost':<30}"
    for m in modes:
        t = totals[m]
        cell_str = f"{t['calls']} calls  {t['secs']:.0f}s"
        cost_row += f"  {_D}{cell_str:>{col}}{_X}"
    print(cost_row)
    print(f"  {_hline()}")


def _print_single_mode_summary(all_records: dict[str, list[dict]]) -> None:
    mode = list(all_records.keys())[0]
    records = all_records[mode]
    total_tests = sum(r.get("approved_tests_count", 0) for r in records)
    ok_funcs = sum(1 for r in records if r.get("approved_tests_count", 0) > 0)
    total_calls = sum(r.get("llm_calls", 0) for r in records)
    total_secs = sum(r.get("elapsed_seconds", 0.0) for r in records)

    print(f"\n  {_hline()}")
    print(
        f"  {_B}Summary ({mode}){_X}"
        f"  {total_tests} tests  {ok_funcs}/{len(records)} functions"
        f"  {_D}{total_calls} calls  {total_secs:.0f}s{_X}"
    )
    print(f"  {_hline()}")


_KNOWN_MODELS = {"8b": MODEL_FAST, "70b": MODEL_STRONG}
_KNOWN_MODES = {"single_agent", "multi_agent"}

if __name__ == "__main__":
    model_label = "mixed"
    model_override: str | None = None
    raw_modes: list[str] = []

    for arg in sys.argv[1:]:
        if arg in _KNOWN_MODELS:
            model_label = arg
            model_override = _KNOWN_MODELS[arg]
        else:
            raw_modes.append(arg)

    modes = raw_modes or ["single_agent", "multi_agent"]
    run_experiment(modes, SAMPLES, model=model_override, model_label=model_label)
