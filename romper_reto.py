"""
romper_reto.py

Breaks the RSA challenge of the course (data/reto_X.txt) in two independent ways:

  1. Chosen-plaintext attack: the message was encrypted character by character
     without padding, so encrypting every possible character with the public key
     and looking the numbers up is enough. The private key is never needed.
  2. Key recovery: factor n with Pollard's rho, compute phi(n) and d = e^(-1) mod phi(n),
     then decrypt normally.

    python romper_reto.py
"""

import time
from pathlib import Path

import modular as md
import rsa

RETO = Path(__file__).resolve().parent / "data" / "reto_X.txt"


def leer_reto(ruta=RETO):
    """Returns (n, e, ciphertext list) from the challenge file."""
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    n, e = (int(x) for x in lineas[0].split(":")[1].split())
    cifrado = [int(x) for x in lineas[3].split()]
    return n, e, cifrado


if __name__ == "__main__":
    n, e, cifrado = leer_reto()
    print(f"Public key: n = {n} ({len(str(n))} digits), e = {e}")
    print(f"Ciphertext: {len(cifrado)} numbers, {len(set(cifrado))} distinct\n")

    t = time.perf_counter()
    texto_1 = rsa.ataque_texto_elegido(cifrado, n, e)
    print(f"1. Chosen-plaintext attack: {1000 * (time.perf_counter() - t):.1f} ms")

    t = time.perf_counter()
    factores = md.factorizar(n)
    d = rsa.romper_clave(n, e)
    texto_2 = rsa.descifrar_cadena_rsa(cifrado, n, d, 0)
    print(f"2. Key recovery: n = {' x '.join(map(str, factores))}, d = {d} "
          f"({1000 * (time.perf_counter() - t):.1f} ms)")

    assert texto_1 == texto_2, "the two attacks disagree"
    print("\nBoth attacks recover the same message:\n")
    print(texto_1)
