"""Tests for the IMAT-LAB command interpreter."""

from io import StringIO
from pathlib import Path

import pytest

import imatlab
from helpers import run

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_course_examples_match_expected_output():
    """ejemplosComandos.txt must produce exactly ejemplosSalida.txt (both from the course)."""
    out = StringIO()
    with open(EXAMPLES / "ejemplosComandos.txt", encoding="utf-8") as fin:
        imatlab.run_commands(fin, out)
    expected = (EXAMPLES / "ejemplosSalida.txt").read_text(encoding="utf-8")
    assert out.getvalue().splitlines() == expected.splitlines()


@pytest.mark.parametrize("command,expected", [
    ("primo(7)", "Sí"), ("primo(-2)", "No"), ("primo(2305843009213693951)", "Sí"),
    ("primos(8,10)", "NE"), ("primos(30,35)", "31"),
    ("factorizar(1)", "1"), ("factorizar(-1)", "-1"), ("factorizar(0)", "0"), ("factorizar(-12)", "2: 2, 3: 1"),
    ("factorizar(28282590191348679547)", "4634630887: 1, 6102447181: 1"),
    ("mcd(4)", "4"), ("mcd(-4)", "4"), ("mcd(4,10,14)", "2"), ("mcd(0,0)", "0"), ("mcd(27,36,45)", "9"),
    ("coprimos(0,1)", "Sí"), ("bezout(6,10)", "(2, 2, -1)"),
    ("pow(0,5,7)", "0"), ("pow(5,0,7)", "1"), ("pow(0,0,7)", "NE"), ("pow(2,3,0)", "NE"), ("pow(3,-1,9)", "NE"),
    ("inv(2,0)", "NE"), ("inv(0,7)", "NE"), ("inv(14,33)", "26"),
    ("euler(15)", "8"), ("legendre(2,0)", "NE"), ("legendre(3,2)", "NE"), ("legendre(2,15)", "NE"),
    ("resolverSistema([2;4;6])", "2 (mod 3)"),
    ("resolverSistema([1;3;4],[1;5;6])", "11 (mod 12)"),
    ("resolverSistema([1;1;5],[1;2;5])", "NE"),
    ("resolverSistema([1;1;0])", "NOP"),
    ("raiz(2,7)", "3, 4"), ("raiz(9,3)", "0"), ("raiz(2,5)", "NE"), ("raiz(0,7)", "0"),
    ("ecCuadratica(1,0,-1,7)", "1, 6"), ("ecCuadratica(1,1,1,2)", "NE"), ("ecCuadratica(0,1,1,7)", "NE"),
])
def test_commands(command, expected):
    assert run(command) == expected


@pytest.mark.parametrize("command", [
    "Legendre(10,3)", "primo(7", "primo(x)", "primo(1,2)", "pow(2,3)", "mcd()", "hola",
    "resolverSistema(1,2,3)",   # used to crash the course version with a TypeError
    "factorizar(3.5)",
])
def test_bad_calls_return_nop_and_never_crash(command):
    assert run(command) == "NOP"


def test_detailed_messages_in_interactive_mode():
    assert run("inv(3,9)", detallado=True) == "NE: no existe inversa"
    assert run("Legendre(10,3)", detallado=True) == "NOP: función no reconocida"
    assert run("pow(2,3)", detallado=True).startswith("NOP: [pow] número de argumentos incorrecto")


def test_batch_stops_at_first_empty_line():
    out = StringIO()
    imatlab.run_commands(StringIO("primo(7)\nprimo(8)\n\nprimo(11)\n"), out)
    assert out.getvalue() == "Sí\nNo\n"
