"""
Check every IMAT-LAB answer on the course benchmark files against SymPy.

    python scripts/check_with_sympy.py                          # this version
    python scripts/check_with_sympy.py --code original/practica1  # course submission

The course only provided input files (no expected outputs), so this script uses
SymPy as an independent oracle: it runs IMAT-LAB on each file and recomputes every
answer with SymPy's own number-theory functions. It prints the number of lines checked
and of mismatches per file, and exits with code 1 if there is any mismatch.
"""

import argparse
import importlib
import sys
from io import StringIO
from math import gcd
from pathlib import Path

import sympy
from sympy import legendre_symbol, totient
from sympy.ntheory import factorint, isprime, sqrt_mod
from sympy.ntheory.modular import solve_congruence

ROOT = Path(__file__).resolve().parent.parent


def parse(line):
    name, args = line.split("(", 1)
    args = args.rstrip(")")
    if name == "resolverSistema":
        blocks = [b.strip("[] ") for b in args.split("],")]
        return name, [tuple(int(x) for x in b.split(";")) for b in blocks]
    return name, [int(x) for x in args.split(",")] if args else []


def expected(name, a):
    """Answer that IMAT-LAB must print, computed with SymPy."""
    if name == "primo":
        return "Sí" if isprime(a[0]) else "No"
    if name == "coprimos":
        return "Sí" if gcd(a[0], a[1]) == 1 else "No"
    if name == "primos":
        ps = list(sympy.primerange(a[0], a[1]))
        return ", ".join(map(str, ps)) if ps else "NE"
    if name == "factorizar":
        if a[0] in (-1, 0, 1):
            return str(a[0])
        f = factorint(abs(a[0]))
        return ", ".join(f"{p}: {e}" for p, e in sorted(f.items()))
    if name == "mcd":
        g = 0
        for x in a:
            g = gcd(g, x)
        return str(g)
    if name == "pow":
        base, exp, p = a
        if p == 0 or (base == 0 and exp == 0):
            return "NE"
        try:
            return str(pow(base, exp, abs(p)))
        except ValueError:  # negative exponent and base not invertible
            return "NE"
    if name == "inv":
        try:
            return str(pow(a[0], -1, abs(a[1])))
        except ValueError:
            return "NE"
    if name == "euler":
        return str(totient(a[0])) if a[0] > 0 else "0"
    if name == "legendre":
        return str(legendre_symbol(a[0] % a[1], a[1]))
    if name == "resolverSistema":
        # Reduce each a*x = b (mod p) to x = r (mod m), then combine
        congruences = []
        for ai, bi, pi in a:
            pi = abs(pi)
            d = gcd(ai, pi)
            if bi % d:
                return "NE"
            m = pi // d
            congruences.append(((bi // d) * pow(ai // d, -1, m) % m if m > 1 else 0, m))
        sol = solve_congruence(*congruences)
        if sol is None:
            return "NE"
        r, m = sol
        return f"{r % m} (mod {m})"
    if name == "raiz":
        roots = sorted(set(sqrt_mod(a[0], a[1], all_roots=True)))
        return ", ".join(map(str, roots)) if roots else "NE"
    if name == "ecCuadratica":
        A, B, C, p = a
        A, B, C = A % p, B % p, C % p
        if A == 0:
            return "NE"
        # Complete the square: (2Ax + B)^2 = B^2 - 4AC
        roots = sqrt_mod((B * B - 4 * A * C) % p, p, all_roots=True)
        if not roots:
            return "NE"
        inv = pow(2 * A, -1, p)
        xs = sorted({(r - B) * inv % p for r in roots})
        return ", ".join(map(str, xs))
    raise ValueError(f"unknown command {name}")


def check(imatlab, path):
    lines = [ln.strip() for ln in open(path, encoding="utf-8") if ln.strip()]
    out = StringIO()
    imatlab.run_commands(StringIO("\n".join(lines) + "\n"), out)
    # The course version prints "NE: <message>" in batch mode; keep only the code
    got = [g.split(":")[0] if g.startswith(("NE", "NOP")) else g for g in out.getvalue().splitlines()]
    bad = [(ln, g, e) for ln, g in zip(lines, got) if g != (e := expected(*parse(ln)))]
    return len(lines), len(got), bad


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*")
    parser.add_argument("--code", default=".", help="folder with imatlab.py and modular.py")
    args = parser.parse_args()
    sys.path.insert(0, str((ROOT / args.code).resolve()))
    imatlab = importlib.import_module("imatlab")

    files = args.files or sorted(str(p) for p in (ROOT / "benchmarks").glob("*Test.txt"))
    total_bad = 0
    for f in files:
        n, n_out, bad = check(imatlab, f)
        total_bad += len(bad) + (n != n_out)
        print(f"{Path(f).name:<20} {n:>7} lines  {len(bad):>3} mismatches")
        for ln, g, e in bad[:5]:
            print(f"    {ln[:80]}\n      IMAT-LAB: {g[:80]}\n      SymPy:    {e[:80]}")
    sys.exit(1 if total_bad else 0)


if __name__ == "__main__":
    main()
