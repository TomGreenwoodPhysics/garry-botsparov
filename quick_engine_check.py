import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "analysis_games"
SUMMARY_FILE = OUTPUT_DIR / "quick_engine_check_summary.txt"


CHECKS = [
    ("quiescence", SCRIPT_DIR / "test_quiescence.py"),
    ("blunders", SCRIPT_DIR / "test_blunders.py"),
    ("position_suite", SCRIPT_DIR / "test_position_suite.py"),
]


def run_check(script_path):
    return subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )


def find_value(output, pattern):
    match = re.search(pattern, output)

    if match is None:
        return "unavailable"

    return match.group(1)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    outputs = {}
    results = {}

    for name, script_path in CHECKS:
        print(f"Running {script_path.name}...")
        result = run_check(script_path)
        results[name] = result
        outputs[name] = result.stdout + result.stderr
        print(outputs[name])

    quiescence_passed = results["quiescence"].returncode == 0
    blunder_output = outputs["blunders"]
    suite_output = outputs["position_suite"]

    summary_lines = [
        f"quiescence passed: {'yes' if quiescence_passed else 'no'}",
        "repeated known blunders: "
        + find_value(blunder_output, r"Repeated known blunders: ([0-9]+)"),
        "matched report Stockfish best: "
        + find_value(blunder_output, r"Matched report Stockfish best: ([0-9]+)"),
        "position suite Stockfish matches: "
        + find_value(suite_output, r"Stockfish matches: ([0-9]+/[0-9]+|unavailable)"),
        "position suite average depth: "
        + find_value(suite_output, r"Average depth: ([0-9.]+)"),
        "position suite average time: "
        + find_value(suite_output, r"Average time per position: ([0-9.]+s)"),
        "position suite average nodes: "
        + find_value(suite_output, r"Average nodes: ([0-9.]+)"),
        "position suite average TT hits: "
        + find_value(suite_output, r"Average TT hits(?: per position)?: ([0-9.]+)"),
        "position suite average aspiration re-searches: "
        + find_value(
            suite_output,
            r"Average aspiration re-searches(?: per position)?: ([0-9.]+)",
        ),
    ]

    summary = "\n".join(summary_lines)
    SUMMARY_FILE.write_text(summary + "\n", encoding="utf-8")

    print("Quick Engine Check Summary")
    print("--------------------------")
    print(summary)

    if not quiescence_passed:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
