"""
How the course version and this version scale with the size of the number.

    python scripts/scaling.py [--timeout 20]
    python scripts/scaling.py --plot-only     # redraw the figure from docs/scaling.csv

Two tasks, for numbers with more and more digits:
  * es_primo(p) on a prime p (the worst case for trial division),
  * factorizar(p * q) on a product of two primes of similar size (an RSA modulus).

Each call runs in a fresh interpreter with a time limit; once a version exceeds it,
larger sizes are skipped for that version. Writes docs/scaling.csv and
docs/figures/scaling.png.
"""

import argparse
import csv
import json
import random
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import modular  # noqa: E402

VERSIONS = {"Course version": ROOT / "original" / "practica1", "This version": ROOT}
COLORS = {"Course version": "#eb6834", "This version": "#2a78d6"}

TIMER = r"""
import json, sys, time
sys.path.insert(0, sys.argv[1])
import modular
func, n = getattr(modular, sys.argv[2]), int(sys.argv[3])
best = float("inf")
for _ in range(3):
    t = time.perf_counter(); func(n); best = min(best, time.perf_counter() - t)
    if best > 1: break
print(json.dumps(best))
"""


def random_prime(digits, rng):
    while True:
        k = rng.randrange(10 ** (digits - 1), 10**digits)
        if modular.es_primo(k):
            return k


def measure(code_dir, func, n, timeout):
    try:
        out = subprocess.run([sys.executable, "-c", TIMER, str(code_dir), func, str(n)],
                             capture_output=True, text=True, timeout=timeout, check=True)
        return json.loads(out.stdout)
    except subprocess.TimeoutExpired:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--plot-only", action="store_true")
    args = parser.parse_args()
    rng = random.Random(0)

    tasks = {
        "es_primo": ("Primality test of a prime", range(6, 41, 2),
                     lambda d: random_prime(d, rng)),
        "factorizar": ("Factoring a product of two primes", range(6, 33, 2),
                       lambda d: random_prime(d // 2, rng) * random_prime(d - d // 2, rng)),
    }
    if args.plot_only:
        with open(ROOT / "docs" / "scaling.csv") as f:
            rows = [dict(r, digits=int(r["digits"]), seconds=float(r["seconds"]) if r["seconds"] else "")
                    for r in csv.DictReader(f)]
        plot(rows, tasks, args.timeout)
        return

    rows = []
    for func, (_, sizes, make) in tasks.items():
        alive = set(VERSIONS)
        for digits in sizes:
            n = make(digits)
            for label, code_dir in VERSIONS.items():
                t = measure(code_dir, func, n, args.timeout) if label in alive else None
                if t is None:
                    alive.discard(label)
                rows.append({"function": func, "digits": digits, "n": n, "version": label,
                             "seconds": t if t is not None else ""})
                print(f"{func:<10} {digits:>2} digits  {label:<15} "
                      f"{f'{t:.5f} s' if t is not None else f'> {args.timeout:.0f} s (skipped)'}")

    with open(ROOT / "docs" / "scaling.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    plot(rows, tasks, args.timeout)


def plot(rows, tasks, timeout):
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#b5b4ae", "axes.labelcolor": "#52514e",
                         "xtick.color": "#52514e", "ytick.color": "#52514e"})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, (func, (title, _, _)) in zip(axes, tasks.items()):
        for label in VERSIONS:
            pts = [(r["digits"], r["seconds"]) for r in rows
                   if r["function"] == func and r["version"] == label and r["seconds"] != ""]
            x, y = zip(*pts)
            ax.plot(x, y, color=COLORS[label], lw=2, marker="o", ms=5, label=label)
            ax.annotate(label, (x[-1], y[-1]), xytext=(6, 0), textcoords="offset points",
                        va="center", fontsize=9, color="#0b0b0b")
            # First size that exceeded the time limit
            over = [r["digits"] for r in rows if r["function"] == func and r["version"] == label
                    and r["seconds"] == "" and r["digits"] > x[-1]]
            if over:
                ax.plot([x[-1], over[0]], [y[-1], timeout], color=COLORS[label], lw=1.5, ls=":")
                ax.plot(over[0], timeout, marker="X", ms=9, color=COLORS[label], mec="white", mew=1)
                ax.annotate(f"> {timeout:.0f} s at {over[0]} digits", (over[0], timeout), xytext=(8, -12),
                            textcoords="offset points", fontsize=8, color="#52514e")
        ax.axhline(timeout, color="#8a8983", lw=1, ls="--")
        ax.text(ax.get_xlim()[0], timeout * 1.6, f"time limit ({timeout:.0f} s)",
                fontsize=8, color="#52514e")
        ax.set_yscale("log")
        ax.set_title(title, fontsize=11, color="#0b0b0b", loc="left")
        ax.set_xlabel("Digits of n")
        ax.grid(axis="y", color="#e4e3df", lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Time per call (s, log scale)")
    axes[1].legend(loc="lower right", frameon=False, fontsize=9)
    fig.tight_layout()
    out = ROOT / "docs" / "figures" / "scaling.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=140, facecolor="white")
    print(f"Saved {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
