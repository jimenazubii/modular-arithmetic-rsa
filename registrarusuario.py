"""
registrarusuario.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP15B
Integrantes:
    - Jimena Zubizarreta Gómez
    - Pilar Pérez Hernández

Descripción:
Registra un usuario de CriptoChat: genera su pareja de claves RSA y las guarda en
Usuarios/pub_<nombre>.txt (n, e y cifras de padding) y Usuarios/priv_<nombre>.txt (d).

Uso:
    python registrarusuario.py                         # pide los datos por teclado
    python registrarusuario.py ana 1000000 10000000 3  # nombre, primo mínimo, primo máximo, padding

La carpeta Usuarios/ contiene claves privadas y está excluida de git (.gitignore).
"""

import os
import re
import sys

from rsa import generar_claves

CARPETA = "Usuarios"
MAX_UNICODE = 0x10FFFF


def nombre_valido(n: str) -> str:
    """
    Comprueba que el nombre no está vacío y solo tiene letras, números, '-' o '_',
    ya que se usa para crear los nombres de los ficheros de claves.
    """
    n = n.strip()
    if not re.fullmatch(r"[\w-]+", n):
        print("Nombre no válido: usa solo letras, números, '-' o '_'")
        sys.exit(1)
    return n


def pedir_entero(mensaje: str, minimo: int = 0) -> int:
    """Pide un entero mayor o igual que minimo hasta que el usuario introduzca uno válido."""
    while True:
        try:
            valor = int(input(mensaje))
            if valor >= minimo:
                return valor
        except ValueError:
            pass
        print(f"Introduce un número entero mayor o igual que {minimo}")


def registrar(nombre: str, min_p: int, max_p: int, cifras_padding: int) -> int:
    """Genera las claves del usuario, las guarda en Usuarios/ y devuelve n."""
    n, e, d = generar_claves(min_p, max_p)   # lanza ValueError si no hay dos primos en el intervalo

    os.makedirs(CARPETA, exist_ok=True)
    with open(f"{CARPETA}/pub_{nombre}.txt", "w") as fichero:
        fichero.write(f"{n}\n{e}\n{cifras_padding}")
    with open(f"{CARPETA}/priv_{nombre}.txt", "w") as fichero:
        fichero.write(f"{d}")
    return n


if __name__ == "__main__":
    if len(sys.argv) == 5:
        nombre = nombre_valido(sys.argv[1])
        min_p, max_p, cifras_padding = map(int, sys.argv[2:])
    else:
        nombre = nombre_valido(input("- Un nombre: "))
        min_p = pedir_entero("- El valor mínimo de cada primo usado para generar sus claves de RSA: ", 2)
        max_p = pedir_entero("- El valor máximo de cada primo usado para generar sus claves de RSA: ", 3)
        while min_p >= max_p:   # el máximo tiene que ser mayor que el mínimo
            print("Error: el mínimo debería ser menor que el máximo")
            min_p = pedir_entero("- El valor mínimo de cada primo: ", 2)
            max_p = pedir_entero("- El valor máximo de cada primo: ", 3)
        cifras_padding = pedir_entero("- El número de cifras de padding para la comunicación con el usuario: ")

    try:
        n = registrar(nombre, min_p, max_p, cifras_padding)
    except ValueError as error:
        print(f"Error: {error}")
        sys.exit(1)

    # Cada carácter se cifra por separado: su código con el padding tiene que ser menor que n
    max_codigo = (n - 1) // 10**cifras_padding
    print(f"Usuario '{nombre}' registrado: n tiene {len(str(n))} cifras.")
    if max_codigo < MAX_UNICODE:
        print(f"Aviso: con {cifras_padding} cifras de padding solo se podrán cifrar caracteres con código "
              f"unicode hasta {max_codigo}. Usa primos más grandes o menos padding si necesitas más.")
