"""
rsa.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP15B
Integrantes:
    - Jimena Zubizarreta Gómez
    - Pilar Pérez Hernández

Descripción:
Librería para la realización de cifrado y descifrado usando el algoritmo RSA, construida
sobre la librería modular.py de la Práctica 1.

Los prototipos de las funciones son los del enunciado. La implementación se reescribió
para este repositorio (ver README): generación de claves con Miller-Rabin, comprobación
de que el mensaje cabe en el módulo, excepciones en lugar de mensajes por pantalla y
ruptura de claves con el método rho de Pollard.

Aviso: es RSA "de libro" con fines didácticos (cifra carácter a carácter y con un padding
muy simple). No debe usarse para proteger información real.
"""

import random
import secrets
from typing import List, Tuple

import modular as md

# Exponente público habitual (primo de Fermat 2^16 + 1): cifrado rápido y seguro con padding
E_ESTANDAR = 65537

# Si el intervalo tiene como mucho este tamaño, se enumeran todos sus primos;
# si es mayor, se eligen impares al azar hasta dar con un primo (Miller-Rabin).
_TAMANO_ENUMERABLE = 200_000

_rng = random.SystemRandom()   # fuente de aleatoriedad del sistema operativo


def _primo_aleatorio(min_primo: int, max_primo: int, distinto_de: int = 0) -> int:
    """Primo aleatorio en [min_primo, max_primo) distinto de distinto_de, para intervalos grandes."""
    # Por el teorema de los números primos, hay un primo cada ln(max) números aprox.,
    # así que este número de intentos falla con probabilidad despreciable.
    intentos = 100 * max_primo.bit_length()
    for _ in range(intentos):
        candidato = _rng.randrange(min_primo, max_primo) | 1     # solo impares
        if candidato < max_primo and candidato != distinto_de and md.es_primo(candidato):
            return candidato
    raise ValueError("No se ha encontrado un primo en el intervalo indicado")


def generar_claves(min_primo: int, max_primo: int) -> Tuple[int, int, int]:
    """Toma dos primos entre min_primo (incluido) y max_primo (excluido) y devuelve
    n,e,d
    donde (n,e) es la clave pública y d la clave privada para RSA

    Args:
        min_primo (int): Límite inferior para los primo p1 y p2 usados en la clave
        max_primo (int): Límite superior para los primo p1 y p2 usados en la clave

    Returns:
        n (int): Módulo para RSA, formado por el producto de dos primos p1 y p2 tales que
            min_primo<=p1, p2 < max_primo
        e (int): Exponente de la clave pública para RSA con módulo n=p1*p2
        d (int): Exponente de la clave privada para RSA con módulo n

    Raises:
        ValueError: Si no es posible encontrar una pareja de primos distintos p1,p2 entre min_primo y max_primo
    """
    if min_primo >= max_primo:
        raise ValueError("El límite inferior debe ser menor que el superior")
    min_primo = max(min_primo, 2)

    if max_primo - min_primo <= _TAMANO_ENUMERABLE:
        primos = md.lista_primos(min_primo, max_primo)
        if len(primos) < 2:
            raise ValueError("No hay dos primos distintos en el intervalo indicado")
        p, q = _rng.sample(primos, 2)
    else:
        p = _primo_aleatorio(min_primo, max_primo)
        q = _primo_aleatorio(min_primo, max_primo, distinto_de=p)

    n = p * q
    phi = (p - 1) * (q - 1)

    # e debe ser coprimo con phi(n) para que exista d = e^(-1) mod phi(n)
    if E_ESTANDAR < phi and md.coprimos(E_ESTANDAR, phi):
        e = E_ESTANDAR
    else:   # claves muy pequeñas (o phi múltiplo de 65537): e aleatorio
        e = _rng.randrange(2, phi)
        while not md.coprimos(e, phi):
            e = _rng.randrange(2, phi)
    d = md.inversa_mod_p(e, phi)
    return n, e, d


def aplicar_padding(m: int, digitos_padding: int) -> int:
    """Dado un mensaje y un número de dígitos de padding, añade
    digitos_padding cifras aleatorias a la derecha del mensaje

    Args:
        m (int): Mensaje sin padding
        digitos_padding (int): Número no negativo de cifras de padding

    Returns:
        int: entero formado por los dígitos de m seguidos de digitos_padding cifras aleatorias.

    Raises:
        ValueError: Si m o digitos_padding son negativos.

    Example:
        aplicar_padding(24,2)=2419
        aplicar_padding(24,2)=2403
        aplicar_padding(24,3)=24718
        aplicar_padding(24,3)=24845
        aplicar_padding(24,0)=24
    """
    if m < 0 or digitos_padding < 0:
        raise ValueError("El mensaje y el número de cifras de padding deben ser no negativos")
    # Desplazar m digitos_padding cifras y sumar un número aleatorio de ese tamaño
    return m * 10**digitos_padding + secrets.randbelow(10**digitos_padding)


def eliminar_padding(m: int, digitos_padding: int) -> int:
    """Dado un mensaje con padding de digitos_padding cifras al
    final del mismo, elimina dichas cifras aleatorias y devuelve
    el resto de cifras del mensaje

    Args:
        m (int): Mensaje con padding
        digitos_padding (int): Número no negativo de cifras de padding

    Returns:
        int: entero resultante de eliminar las últimas digitos_padding cifras de m.

    Raises:
        ValueError: Si digitos_padding es negativo.

    Example:
        eliminar_padding(2454,1)=245
        eliminar_padding(2454,2)=24
        eliminar_padding(2454,3)=2
        eliminar_padding(2432,2)=24
        eliminar_padding(2432,0)=2432
    """
    if digitos_padding < 0:
        raise ValueError("El número de cifras de padding debe ser no negativo")
    return m // 10**digitos_padding


def cifrar_rsa(m: int, n: int, e: int, digitos_padding: int) -> int:
    """Dado un mensaje m entero, un módulo y exponente que formen parte
    de una clave pública de RSA, con m<n*10^{-digitos_padding}, y un número
    de dígitos de padding, aplica el padding al mensaje y lo cifra
    usando RSA con módulo n y exponente e.

    Args:
        m (int): Mensaje original claro (sin padding)
        n (int): Módulo de la clave pública de RSA
        e (int): Exponente de la clave pública de RSA
        digitos_padding (int): Número no negativo de cifras de padding

    Returns:
        int: entero resultante de agregar el padding a m y aplicar RSA.

    Raises:
        ValueError: Si el mensaje con padding no es menor que n (no se podría descifrar).
    """
    x = aplicar_padding(m, digitos_padding)
    if x >= n:
        raise ValueError(f"El mensaje con padding ({x}) debe ser menor que n ({n}): "
                         "usa una clave más grande o menos cifras de padding")
    return md.potencia_mod_p(x, e, n)


def descifrar_rsa(c: int, n: int, d: int, digitos_padding: int) -> int:
    """Dado un cifrado c entero que haya sido cifrado con RSA usando
    digitos_padding cifras de padding al final del mensaje y el
    módulo y exponente privado, n y d que formen la clave privada de RSA cuya pareja se
    utilizó para cifrar c, descifra c y elimina el padding, devolviendo
    el mensaje original.

    Args:
        c (int): Mensaje cifrado
        n (int): Módulo de la clave pública de RSA usado para cifrar
        d (int): Exponente de la clave privada de RSA cuya pareja se utilizó para cifrar c
        digitos_padding (int): Número no negativo de cifras de padding usados para cifrar c

    Returns:
        int: entero resultante de descifrar c usando RSA con módulo n y exponente d y después eliminar el padding al resultado.

    Raises: None
    """
    return eliminar_padding(md.potencia_mod_p(c, d, n), digitos_padding)


def codificar_cadena(s: str) -> List[int]:
    """Convierte una cadena de caracteres a la lista de
    enteros que representa el valor unicode cada uno de sus caracteres.

    Args:
        s (str): cadena en texto plano

    Returns:
        List[int]: lista de enteros que representan el código unicode de cada carácter de la cadena s.

    Raises: None.

    Example:
        codificar_cadena("¡Hola mundo!")=[161, 72, 111, 108, 97, 32, 109, 117, 110, 100, 111, 33]
    """
    return [ord(caracter) for caracter in s]


def decodificar_cadena(m: List[int]) -> str:
    """Convierte una lista de enteros que representen caracteres unicode
    en la cadena que representan.

    Args:
        m (List[int]): lista de enteros que representan los códigos unicode de una cadena de caracteres.

    Returns:
        str: cadena que representan

    Raises:
        ValueError: Si alguno de los enteros no representa un caracter unicode válido.

    Example:
        decodificar_cadena([161, 72, 111, 108, 97, 32, 109, 117, 110, 100, 111, 33])="¡Hola mundo!"
    """
    try:
        return "".join(chr(c) for c in m)
    except (ValueError, OverflowError) as error:   # código negativo o mayor que 0x10FFFF
        raise ValueError("Alguno de los enteros no representa un carácter unicode válido") from error


def cifrar_cadena_rsa(s: str, n: int, e: int, digitos_padding: int) -> List[int]:
    """Cifra carácter a carácter una cadena de caracteres usando RSA con clave púbica (n,e)
    y digitos_padding cifras de padding al final del mensaje y devuelve la lista de enteros
    que representan el mensaje cifrado correspondiente.

    Args:
        s (str): texto claro
        n (int): módulo para RSA
        e (int): clave pública para RSA
        digitos_padding (int): número no negativo de dígitos de padding que deben usarse para el cifrado del mensaje.

    Returns:
        List[int]: lista de enteros que representa el mensaje cifrado con RSA para la clave dada.

    Raises:
        ValueError: Si algún carácter con su padding no cabe en el módulo n.
    """
    return [cifrar_rsa(m, n, e, digitos_padding) for m in codificar_cadena(s)]


def descifrar_cadena_rsa(cList: List[int], n: int, d: int, digitos_padding: int) -> str:
    """Dado un mensaje cifrado con RSA usando la clave pública cuya clave privada asociada es (n,d)
    y digitos_padding cifras de padding al final del mensaje, devuelve la cadena orignal.

    Args:
        cList (List[int]): lista de enteros que representan el mensaje cifrado
        n (int): módulo para RSA
        d (int): clave privada para RSA
        digitos_padding (int): número no negativo de dígitos de padding usados para el cifrado de cList.

    Returns:
        str: cadena que representa el texto claro correspondiente al mensaje cifrado cList.

    Raises:
        ValueError: Si, tras decodificar, alguno de los enteros del mensaje no representa un caracter unicode válido.
    """
    return decodificar_cadena([descifrar_rsa(c, n, d, digitos_padding) for c in cList])


def romper_clave(n: int, e: int) -> int:
    """A partir de una clave pública válida (n,e), recupera la clave privada d tal que
    de = 1 (mod phi(n)).

    Calcula phi(n) factorizando n (rho de Pollard en modular.factorizar), así que es viable
    para módulos de hasta unas 30-40 cifras, no para claves RSA reales.

    Args:
        n (int): módulo para RSA
        e (int): clave pública para RSA

    Returns:
        int: clave privada d

    Raises:
        ValueError: Si no existe ninguna clave privada d compatible con la clave pública (n,e).
    """
    if n < 2:
        raise ValueError("n debe ser mayor que 1")
    phi = md.euler(n)
    try:
        return md.inversa_mod_p(e, phi)
    except ZeroDivisionError as error:
        raise ValueError(f"e = {e} no es invertible módulo phi(n) = {phi}: "
                         "no existe clave privada compatible") from error


# Alfabeto que se prueba primero en el ataque: ASCII imprimible, tildes y eñes, saltos de línea
_ALFABETO_HABITUAL = [chr(c) for c in range(32, 127)] + list("ñÑäëïöüáéíóúÁÉÍÓÚ¿¡\n\t")


def ataque_texto_elegido(cList: List[int], n: int, e: int) -> str:
    """Ejecuta un ataque de texto claro elegido sobre un mensaje que ha sido cifrado
    con RSA plano sin usar padding a partir de su clave pública.

    Sin padding, RSA es determinista: cada carácter se cifra siempre igual. Basta con cifrar
    con la clave pública cada carácter posible y buscar cada número de cList en esa tabla.
    Se prueba primero un alfabeto habitual y, si quedan números sin identificar, todo el
    plano multilingüe básico de Unicode.

    Args:
        cList (List[int]): lista de enteros que representan el mensaje cifrado
        n (int): módulo para RSA
        e (int): clave pública para RSA

    Returns:
        str: texto plano descifrado para el mensaje cifrado cList

    Raises:
        ValueError: Si el mensaje no se corresponde con ningún texto plano que haya sido codificado con RSA sin padding.
    """
    tabla = {cifrar_rsa(ord(ch), n, e, 0): ch for ch in _ALFABETO_HABITUAL if ord(ch) < n}
    if any(c not in tabla for c in cList):
        for codigo in range(min(0x10000, n)):
            if not 0xD800 <= codigo <= 0xDFFF:      # los sustitutos no son caracteres
                tabla.setdefault(md.potencia_mod_p(codigo, e, n), chr(codigo))
    desconocidos = {c for c in cList if c not in tabla}
    if desconocidos:
        raise ValueError(f"{len(desconocidos)} números del mensaje no corresponden a ningún carácter "
                         "cifrado sin padding con esta clave")
    return "".join(tabla[c] for c in cList)
