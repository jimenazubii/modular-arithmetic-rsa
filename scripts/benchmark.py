"""
Time IMAT-LAB on the course benchmark files, like the course's imatlab_benchmark.py.

    python scripts/benchmark.py [--runs 10] [--compare-original]

For each file it reports the mean time of run_commands over --runs runs (file
read and output written in memory, imports excluded) and the course's reference
times (bronze / silver / gold, measured on the ICAI lab computers, so only roughly
comparable with other machines). With --compare-original it also times the
version submitted for the course (original/practica1). Results are written to
docs/benchmark.csv.
"""

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Reference times from the assignment, in seconds: (bronze, silver, gold)
REFERENCE = {
    "primosTest": (10, 4.3, 0.730),
    "factorTest": (7.5, 2.33, 1.99),
    "mcdTest": (2.7, 1.5, 1.0),
    "potenciaTest": (0.800, 0.220, 0.120),
    "invTest": (6.5, 4.2, 3.125),
    "eulerTest": (5.5, 1.06, 0.779),
    "sistemaTest": (4.5, 1.5, 0.988),
    "cuadraticaTest": (1.1, 0.355, 0.218),
}

# Runs in a fresh interpreter so that each version imports its own modular.py
TIMER = r"""
import io, json, sys, timeit
sys.path.insert(0, sys.argv[1])
import imatlab
text = open(sys.argv[2], encoding="utf-8").read()
runs = int(sys.argv[3])
t = timeit.timeit(lambda: imatlab.run_commands(io.StringIO(text), io.StringIO()), number=runs)
print(json.dumps(t / runs))
"""


def time_file(code_dir, path, runs):
    out = subprocess.run([sys.executable, "-c", TIMER, str(code_dir), str(path), str(runs)],
                         capture_output=True, text=True, check=True, cwd=ROOT)
    return json.loads(out.stdout)


def tier(seconds, ref):
    for name, limit in zip(("gold", "silver", "bronze"), reversed(ref)):
        if seconds <= limit:
            return name
    return "-"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--compare-original", action="store_true")
    args = parser.parse_args()

    versions = {"this version": ROOT}
    if args.compare_original:
        versions["course version"] = ROOT / "original" / "practica1"

    rows = []
    for name, ref in REFERENCE.items():
        path = ROOT / "benchmarks" / f"{name}.txt"
        row = {"file": f"{name}.txt", "gold_s": ref[2]}
        for label, code_dir in versions.items():
            t = time_file(code_dir, path, args.runs)
            row[f"{label} (s)"] = round(t, 4)
            row[f"{label} tier"] = tier(t, ref)
        rows.append(row)
        print("  ".join(f"{k}: {v}" for k, v in row.items()))

    out = ROOT / "docs" / "benchmark.csv"
    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
