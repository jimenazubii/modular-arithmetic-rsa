"""Tests for rsa.py (course test cases plus round-trips, errors and the challenge)."""

from pathlib import Path

import pytest

import modular
import rsa

DATA = Path(__file__).resolve().parent.parent / "data" / "reto_X.txt"


def test_codificar_decodificar():
    codes = [161, 72, 111, 108, 97, 32, 109, 117, 110, 100, 111, 33]
    assert rsa.codificar_cadena("¡Hola mundo!") == codes
    assert rsa.decodificar_cadena(codes) == "¡Hola mundo!"


@pytest.mark.parametrize("codes", [[-1], [0x110000], [10**30]])
def test_decodificar_invalid_raises(codes):
    with pytest.raises(ValueError):
        rsa.decodificar_cadena(codes)


@pytest.mark.parametrize("m,k,expected", [(2454, 1, 245), (2454, 2, 24), (2454, 3, 2), (2432, 2, 24), (2432, 0, 2432)])
def test_eliminar_padding(m, k, expected):
    assert rsa.eliminar_padding(m, k) == expected


@pytest.mark.parametrize("m", range(10))
@pytest.mark.parametrize("k", range(4))
def test_padding_round_trip(m, k):
    x = rsa.aplicar_padding(m, k)
    assert rsa.eliminar_padding(x, k) == m and x < (m + 1) * 10**k


def test_padding_negative_raises():
    with pytest.raises(ValueError):
        rsa.aplicar_padding(5, -1)


@pytest.mark.parametrize("rnd", range(10))
def test_generar_claves(rnd):
    n, e, d = rsa.generar_claves(1000, 10000)
    p, q = modular.factorizar(n)
    assert 1000 <= p < 10000 and 1000 <= q < 10000 and p != q
    assert e * d % modular.euler(n) == 1


def test_generar_claves_large_interval_uses_random_primes():
    n, e, d = rsa.generar_claves(10**29, 10**30)     # n has ~60 digits
    assert len(str(n)) >= 58 and e == rsa.E_ESTANDAR
    m = 123456789
    assert rsa.descifrar_rsa(rsa.cifrar_rsa(m, n, e, 5), n, d, 5) == m


def test_generar_claves_narrow_interval():
    # Only four primes in [10^15, 10^15 + 200): the course version listed them by trial division
    primes = {10**15 + 37, 10**15 + 91, 10**15 + 159, 10**15 + 187}
    n, _, _ = rsa.generar_claves(10**15, 10**15 + 200)
    p, q = modular.factorizar(n)
    assert {p, q} <= primes and p != q


@pytest.mark.parametrize("lo,hi", [(10, 10), (20, 10), (24, 29), (8, 11)])
def test_generar_claves_not_enough_primes(lo, hi):
    with pytest.raises(ValueError):
        rsa.generar_claves(lo, hi)


@pytest.mark.parametrize("n,e,d", [(809570247883, 77204266853, 42840500717)])
def test_romper_clave(n, e, d):
    assert rsa.romper_clave(n, e) == d


@pytest.mark.parametrize("rnd", range(5))
def test_generar_romper_claves(rnd):
    n, e, d = rsa.generar_claves(10**8, 10**9)      # 17-18 digit modulus
    assert rsa.romper_clave(n, e) == d


def test_romper_clave_impossible():
    with pytest.raises(ValueError):
        rsa.romper_clave(15, 2)      # phi(15) = 8 is even, so e = 2 has no inverse


@pytest.mark.parametrize("padding", [0, 2, 4])
def test_string_round_trip(padding):
    n, e, d = rsa.generar_claves(10**6, 10**7)
    text = "Matemática Discreta: ¿cifrará bien la ñ? 😀"
    c = rsa.cifrar_cadena_rsa(text, n, e, padding)
    assert rsa.descifrar_cadena_rsa(c, n, d, padding) == text


def test_padding_makes_encryption_non_deterministic():
    n, e, _ = rsa.generar_claves(10**6, 10**7)
    assert len(set(rsa.cifrar_cadena_rsa("aaaaaaaaaa", n, e, 4))) > 1
    assert len(set(rsa.cifrar_cadena_rsa("aaaaaaaaaa", n, e, 0))) == 1


def test_message_too_large_for_modulus_raises():
    n, e, _ = rsa.generar_claves(10, 30)          # n < 900
    with pytest.raises(ValueError):
        rsa.cifrar_rsa(ord("a"), n, e, 2)        # 97xx > n: could never be decrypted


def test_chosen_plaintext_attack():
    n, e, _ = rsa.generar_claves(10**5, 10**6)
    text = "Ataque de texto elegido: ¡funciona sin padding! 日本"
    assert rsa.ataque_texto_elegido(rsa.cifrar_cadena_rsa(text, n, e, 0), n, e) == text


def test_chosen_plaintext_attack_fails_with_padding():
    n, e, _ = rsa.generar_claves(10**5, 10**6)
    with pytest.raises(ValueError):
        rsa.ataque_texto_elegido(rsa.cifrar_cadena_rsa("hola", n, e, 3), n, e)


def test_course_challenge_both_attacks_agree():
    lines = DATA.read_text(encoding="utf-8").splitlines()
    n, e = map(int, lines[0].split(":")[1].split())
    c = [int(x) for x in lines[3].split()]
    d = rsa.romper_clave(n, e)
    plain = rsa.descifrar_cadena_rsa(c, n, d, 0)
    assert rsa.ataque_texto_elegido(c, n, e) == plain
    assert len(plain) == len(c) == 759
