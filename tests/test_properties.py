"""Property-based tests: modular.py against SymPy on random inputs (Hypothesis)."""

from math import gcd

import sympy
from hypothesis import given, settings, strategies as st
from sympy import legendre_symbol
from sympy.ntheory import factorint, isprime, sqrt_mod
from sympy.ntheory.modular import solve_congruence

import modular

ints = st.integers(min_value=-10**30, max_value=10**30)
moduli = st.integers(min_value=1, max_value=10**12)
odd_primes = st.integers(min_value=3, max_value=10**9).map(lambda k: sympy.nextprime(k))


@given(st.integers(min_value=-10, max_value=10**40))
def test_es_primo(n):
    assert modular.es_primo(n) == isprime(n)


@given(st.integers(min_value=-10**24, max_value=10**24))
@settings(max_examples=60, deadline=None)
def test_factorizar(n):
    assert modular.factorizar(n) == ({} if n in (-1, 0, 1) else factorint(abs(n)))


@given(st.integers(min_value=-1000, max_value=10**7), st.integers(min_value=0, max_value=5000))
def test_lista_primos(a, width):
    assert modular.lista_primos(a, a + width) == list(sympy.primerange(a, a + width))


@given(ints, ints)
def test_bezout(a, b):
    d, x, y = modular.bezout(a, b)
    assert d == gcd(a, b) and a * x + b * y == d


@given(ints, st.integers(min_value=-10**6, max_value=10**6), moduli)
def test_potencia(base, exp, p):
    try:
        expected = pow(base, exp, p)
    except ValueError:   # negative exponent, base not invertible
        expected = None
    if base == 0 and exp == 0:
        expected = None
    if expected is None:
        try:
            modular.potencia_mod_p(base, exp, p)
            assert False, "should have raised"
        except ZeroDivisionError:
            pass
    else:
        assert modular.potencia_mod_p(base, exp, p) == expected


@given(st.integers(min_value=1, max_value=10**15))
@settings(deadline=None)
def test_euler(n):
    assert modular.euler(n) == sympy.totient(n)


@given(ints, odd_primes)
def test_legendre_and_raiz(n, p):
    assert modular.legendre(n, p) == legendre_symbol(n % p, p)
    roots = sqrt_mod(n, p, all_roots=True)
    if roots:
        assert modular.raiz_mod_p(n, p) in roots
    else:
        try:
            modular.raiz_mod_p(n, p)
            assert False, "should have raised"
        except modular.IncompatibleEquationError:
            pass


@given(st.lists(st.tuples(st.integers(-10**6, 10**6), st.integers(-10**6, 10**6),
                          st.integers(1, 10**4)), min_size=1, max_size=5))
def test_resolver_sistema(eqs):
    alist, blist, plist = map(list, zip(*eqs))
    # Brute-force reference: reduce each congruence, then let SymPy combine them
    congruences, ok = [], True
    for a, b, p in eqs:
        d = gcd(a, p)
        if b % d:
            ok = False
            break
        m = p // d
        congruences.append(((b // d) * pow(a // d, -1, m) % m if m > 1 else 0, m))
    sol = solve_congruence(*congruences) if ok else None
    try:
        r, m = modular.resolver_sistema_congruencias(alist, blist, plist)
        assert sol is not None and (r, m) == (sol[0] % sol[1], sol[1])
    except modular.IncompatibleEquationError:
        assert sol is None
