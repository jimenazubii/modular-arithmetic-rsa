"""
criptochat.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP15B
Integrantes:
    - Jimena Zubizarreta Gómez
    - Pilar Pérez Hernández

Descripción:
Chat cifrado con RSA entre dos usuarios registrados con registrarusuario.py.

Uso:
    python criptochat.py <usuario1> <usuario2>

usuario1 cifra los mensajes que envía con la clave pública de usuario2 y descifra los
que recibe con su propia clave privada.
"""

import os
import sys

from rsa import cifrar_cadena_rsa, descifrar_cadena_rsa

CARPETA = "Usuarios"


def cargar_clave_publica(usuario: str):
    """
    Carga la clave pública de un usuario desde la carpeta 'Usuarios'.
    Si el archivo existe, devuelve una tupla (n, e, padding), si no, devuelve None.
    """
    ruta = f"{CARPETA}/pub_{usuario}.txt"
    if not os.path.exists(ruta):
        return None
    with open(ruta, "r") as f:
        n, e, n_padding = (int(linea) for linea in f.read().split())
    return (n, e, n_padding)


def cargar_clave_privada(usuario: str):
    """
    Carga la clave privada de un usuario desde la carpeta 'Usuarios'.
    Si el archivo existe, devuelve d (int), si no, devuelve None.
    """
    ruta = f"{CARPETA}/priv_{usuario}.txt"
    if not os.path.exists(ruta):
        return None
    with open(ruta, "r") as f:
        return int(f.read().strip())


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso correcto: python criptochat.py <usuario1> <usuario2>")
        sys.exit(2)
    usuario1, usuario2 = sys.argv[1], sys.argv[2]

    # Cargamos las claves de los usuarios
    clave_pub_u1 = cargar_clave_publica(usuario1)
    clave_priv_u1 = cargar_clave_privada(usuario1)
    clave_pub_u2 = cargar_clave_publica(usuario2)

    # Comprobamos que existan las claves necesarias
    if not clave_pub_u1:
        sys.exit(f"La clave pública de {usuario1} no existe. Regístralo con registrarusuario.py")
    if not clave_pub_u2:
        sys.exit(f"La clave pública de {usuario2} no existe. Regístralo con registrarusuario.py")
    if not clave_priv_u1:
        sys.exit(f"La clave privada de {usuario1} no existe.")

    opcion = ""
    while opcion != "S":
        try:
            opcion = input("¿Qué quieres hacer: cifrar (C), descifrar (D) o salir (S)? ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if opcion == "C":
            # usuario1 envía un mensaje a usuario2: se cifra con la clave pública de usuario2
            mensaje = input("Introduce el texto que deseas cifrar: ")
            n, e, padding = clave_pub_u2
            try:
                cifrado = cifrar_cadena_rsa(mensaje, n, e, padding)
            except ValueError as error:   # algún carácter con padding no cabe en n
                print(f"No se puede cifrar: {error}")
                continue
            print("Mensaje cifrado:", " ".join(str(c) for c in cifrado))

        elif opcion == "D":
            # usuario1 descifra un mensaje recibido con su clave privada
            texto = input("Introduce el mensaje cifrado que deseas descifrar: ")
            n, _, padding = clave_pub_u1
            try:
                cifrado = [int(c) for c in texto.split()]
                print("Mensaje descifrado:", descifrar_cadena_rsa(cifrado, n, clave_priv_u1, padding))
            except ValueError:
                print("El mensaje no es válido: deben ser números separados por espacios, "
                      f"cifrados con la clave pública de {usuario1}.")

        elif opcion != "S":
            print("Opción no válida. Por favor, selecciona C, D o S.")
