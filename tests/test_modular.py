"""Unit tests for modular.py (cases from the course tests, completed and extended)."""

import pytest

import modular
from excepciones import IncompatibleEquationError, NotQuadraticResidueError


@pytest.mark.parametrize("n,expected", [
    (2, True), (3, True), (4, False), (5, True), (0, False), (1, False), (-1, False), (-7, False),
    (20, False), (97, True), (999_983, True), (1_000_001, False),
    (561, False),                       # Carmichael number: fools the Fermat test
    (3_215_031_751, False),             # strong pseudoprime to bases 2, 3, 5 and 7
    (2**61 - 1, True), (2**89 - 1, True), (2**127 - 1, True),   # Mersenne primes
    ((2**61 - 1) * (2**89 - 1), False),
])
def test_es_primo(n, expected):
    assert modular.es_primo(n) == expected


@pytest.mark.parametrize("a,b,expected", [
    (1, 11, [2, 3, 5, 7]), (8, 10, []), (2, 2, []), (4, 4, []), (10, 20, [11, 13, 17, 19]),
    (20, 30, [23, 29]), (30, 35, [31]), (0, 1, []), (-10, 3, [2]), (5, 3, []),
    (10**12, 10**12 + 100, [10**12 + 39, 10**12 + 61, 10**12 + 63, 10**12 + 91]),
])
def test_lista_primos(a, b, expected):
    assert modular.lista_primos(a, b) == expected


def test_lista_primos_counts():
    assert len(modular.lista_primos(0, 10**6)) == 78_498          # pi(10^6)
    assert len(modular.lista_primos(10**15, 10**15 + 1000)) == 24  # narrow window, Miller-Rabin path


@pytest.mark.parametrize("n,expected", [
    (1, {}), (-1, {}), (0, {}), (2, {2: 1}), (12, {2: 2, 3: 1}), (-12, {2: 2, 3: 1}),
    (16, {2: 4}), (25, {5: 2}), (100, {2: 2, 5: 2}), (97, {97: 1}),
    (1009**2, {1009: 2}),
    (4634630887 * 6102447181, {4634630887: 1, 6102447181: 1}),  # modulus of the RSA challenge
    ((2**31 - 1) ** 3 * 2**5, {2: 5, 2**31 - 1: 3}),
])
def test_factorizar(n, expected):
    assert modular.factorizar(n) == expected


@pytest.mark.parametrize("a,b,expected", [(10, 15, 5), (5, 0, 5), (0, 0, 0), (27, 36, 9), (101, 103, 1), (-12, 18, 6)])
def test_mcd(a, b, expected):
    assert modular.mcd(a, b) == expected


@pytest.mark.parametrize("a,b,d", [(6, 10, 2), (21, 14, 7), (25, 49, 1), (12, 18, 6), (-6, 10, 2), (6, -10, 2), (0, 0, 0), (0, -5, 5)])
def test_bezout(a, b, d):
    g, x, y = modular.bezout(a, b)
    assert g == d and a * x + b * y == g


def test_bezout_large_inputs_no_recursion_limit():
    # Consecutive Fibonacci numbers are Euclid's worst case: ~1,400 steps here
    f = [0, 1]
    while len(f) < 2000:
        f.append(f[-1] + f[-2])
    g, x, y = modular.bezout(f[-1], f[-2])
    assert g == 1 and f[-1] * x + f[-2] * y == 1


@pytest.mark.parametrize("nlist,d", [([4, 10, 14], 2), ([13, 17, 19], 1), ([12, 18, 24], 6), ([7, 7, 7], 7),
                                     ([0, 6, -9], 3), ([-4], 4), ([], 0)])
def test_mcd_n_and_bezout_n(nlist, d):
    assert modular.mcd_n(nlist) == d
    g, coef = modular.bezout_n(nlist)
    assert g == d and len(coef) == len(nlist)
    assert sum(c * a for c, a in zip(coef, nlist)) == g


@pytest.mark.parametrize("a,b,expected", [(14, 20, False), (14, 15, True), (17, 19, True), (25, 49, True),
                                          (0, 5, False), (0, 1, True), (13, 13, False)])
def test_coprimos(a, b, expected):
    assert modular.coprimos(a, b) == expected


@pytest.mark.parametrize("base,exp,p,expected", [
    (2, 3, 7, 1), (4, 4, 9, 4), (7, 128, 13, 3), (2, 5, 3, 2), (-3, -8, 7, 4), (100, 100, 3, 1),
    (0, 5, 7, 0),        # the course version raised an error here
    (5, 0, 7, 1),        # ... and here
    (5, 3, 1, 0), (3, 4, -7, 4),
])
def test_potencia_mod_p(base, exp, p, expected):
    assert modular.potencia_mod_p(base, exp, p) == expected == pow(base, exp, abs(p))


@pytest.mark.parametrize("base,exp,p", [(2, 3, 0), (0, 0, 7), (3, -1, 9)])
def test_potencia_mod_p_errors(base, exp, p):
    with pytest.raises(ZeroDivisionError):
        modular.potencia_mod_p(base, exp, p)


@pytest.mark.parametrize("n,p,expected", [(2, 7, 4), (14, 33, 26), (8, 15, 2), (7, 13, 2), (4, 9, 7), (5, 9, 2), (-1, 7, 6)])
def test_inversa_mod_p(n, p, expected):
    assert modular.inversa_mod_p(n, p) == expected


@pytest.mark.parametrize("n,p", [(2, 0), (3, 9), (0, 7)])
def test_inversa_mod_p_errors(n, p):
    with pytest.raises(ZeroDivisionError):
        modular.inversa_mod_p(n, p)


@pytest.mark.parametrize("n,expected", [(1, 1), (7, 6), (15, 8), (36, 12), (97, 96), (2**20, 2**19), (0, 0), (-5, 0),
                                        (4634630887 * 6102447181, 4634630886 * 6102447180)])
def test_euler(n, expected):
    assert modular.euler(n) == expected


@pytest.mark.parametrize("n,p,expected", [(2, 5, -1), (2, 7, 1), (10, 5, 0), (10, 3, 1), (-1, 5, 1), (-1, 7, -1)])
def test_legendre(n, p, expected):
    assert modular.legendre(n, p) == expected


def test_legendre_errors():
    with pytest.raises(ZeroDivisionError):
        modular.legendre(2, 0)
    with pytest.raises(ValueError):
        modular.legendre(3, 2)
    with pytest.raises(ValueError):     # 15 is not prime: Euler's criterion gives neither 1 nor -1
        modular.legendre(2, 15)


@pytest.mark.parametrize("alist,blist,plist,expected", [
    ([2], [3], [5], (4, 5)),
    ([2], [4], [6], (2, 3)),                     # 2x = 4 (mod 6)  <=>  x = 2 (mod 3)
    ([1, 4], [1, 7], [3, 11], (10, 33)),
    ([1, 1, 1], [2, 3, 2], [3, 5, 7], (23, 105)),  # Sunzi's classic problem
    ([1, 1], [3, 5], [4, 6], (11, 12)),           # moduli not coprime
    ([1, 1], [1, 1], [6, 6], (1, 6)),
])
def test_resolver_sistema(alist, blist, plist, expected):
    assert modular.resolver_sistema_congruencias(alist, blist, plist) == expected


@pytest.mark.parametrize("alist,blist,plist", [([2], [3], [4]), ([1, 1], [1, 2], [5, 5]), ([1, 1], [0, 1], [4, 6]), ([0], [1], [7])])
def test_resolver_sistema_incompatible(alist, blist, plist):
    with pytest.raises(IncompatibleEquationError):
        modular.resolver_sistema_congruencias(alist, blist, plist)


def test_resolver_sistema_invalid_input():
    with pytest.raises(ValueError):
        modular.resolver_sistema_congruencias([1, 2], [1], [3])
    with pytest.raises(ValueError):
        modular.resolver_sistema_congruencias([], [], [])
    with pytest.raises(ValueError):
        modular.resolver_sistema_congruencias([1], [1], [0])


@pytest.mark.parametrize("n,p", [(2, 7), (4, 5), (9, 3), (5, 2), (10, 13), (2, 17), (3, 73), (1_002, 1_000_000_007)])
def test_raiz_mod_p(n, p):
    x = modular.raiz_mod_p(n, p)
    assert 0 <= x < p and x * x % p == n % p


@pytest.mark.parametrize("p", [
    2**61 - 1, 2**127 - 1,          # p = 3 (mod 4): direct formula
    998_244_353, 10**9 + 9,         # p = 1 (mod 4): Cipolla's algorithm
    2**255 - 19,                    # 1 (mod 4), 77 digits
])
def test_raiz_mod_p_large_primes(p):
    for k in (2, 12345, 10**18 + 3):
        n = k * k % p
        x = modular.raiz_mod_p(n, p)
        assert x * x % p == n and x in (k % p, -k % p)


@pytest.mark.parametrize("n,p", [(2, 5), (3, 7), (2, 11), (1_000, 1_000_000_007)])
def test_raiz_mod_p_no_root(n, p):
    with pytest.raises(NotQuadraticResidueError):
        modular.raiz_mod_p(n, p)


@pytest.mark.parametrize("a,b,c,p,expected", [
    (4, 1, 5, 11, (3, 5)), (1, 2, 1, 11, (10, 10)), (1, 0, -1, 7, (1, 6)), (1, 1, 1, 2, None), (1, 1, 0, 2, (0, 1)),
])
def test_ecuacion_cuadratica(a, b, c, p, expected):
    if expected is None:
        with pytest.raises(IncompatibleEquationError):
            modular.ecuacion_cuadratica(a, b, c, p)
    else:
        assert modular.ecuacion_cuadratica(a, b, c, p) == expected


@pytest.mark.parametrize("a,b,c,p", [(4, 1, 3, 11), (1, 0, 1, 7), (11, 1, 1, 11)])
def test_ecuacion_cuadratica_no_solution(a, b, c, p):
    with pytest.raises(IncompatibleEquationError):
        modular.ecuacion_cuadratica(a, b, c, p)
