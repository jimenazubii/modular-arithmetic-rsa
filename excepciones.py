"""
excepciones.py

Excepciones de IMAT-LAB y de la librería modular.

    - NE  (No Existe): el problema no tiene solución.
    - NOP: la llamada al comando es incorrecta o el comando no existe.
    - IncompatibleEquationError: una ecuación o sistema no tiene solución.
      El enunciado exige que cualquier otra excepción de la librería la extienda.
"""


class NE(Exception):
    pass


class NOP(Exception):
    pass


class IncompatibleEquationError(Exception):
    pass


class NotQuadraticResidueError(IncompatibleEquationError):
    """n no es un cuadrado módulo p, así que x^2 = n (mod p) no tiene solución."""
