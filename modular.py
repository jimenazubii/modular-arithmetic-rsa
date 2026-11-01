"""
modular.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP15B
Integrantes:
    - Jimena Zubizarreta Gómez
    - Pilar Pérez Hernández

Descripción:
Librería para la realización de cálculos y resolución de problemas de aritmética modular.

Las funciones públicas mantienen los prototipos exigidos por el enunciado. La versión
entregada en la asignatura está en original/practica1/modular.py; los cambios respecto a
ella se resumen en el README (sección "What changed").
"""

import random
from itertools import compress
from math import gcd, isqrt
from typing import Dict, List, Tuple

from excepciones import IncompatibleEquationError, NotQuadraticResidueError


# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------

# Primos menores que 1000, para la división por tentativa inicial
def _criba(lim: int) -> List[int]:
    """Criba de Eratóstenes: lista de primos <= lim."""
    if lim < 2:
        return []
    es_p = bytearray([1]) * (lim + 1)
    es_p[0] = es_p[1] = 0
    for i in range(2, isqrt(lim) + 1):
        if es_p[i]:
            # Tachamos todos los múltiplos de i desde i^2 de una sola vez
            es_p[i * i::i] = bytes(len(range(i * i, lim + 1, i)))
    return list(compress(range(lim + 1), es_p))


_PRIMOS_PEQUENOS = _criba(1000)

# Con estas 12 bases, Miller-Rabin es determinista para n < 3.317 * 10^24
_BASES_MR = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
_LIMITE_MR_DETERMINISTA = 3317044064679887385961981
_RONDAS_MR_EXTRA = 20


def _miller_rabin(n: int, bases) -> bool:
    """Test de Miller-Rabin para n impar > 37 con las bases dadas."""
    # Escribimos n - 1 = d * 2^s con d impar
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in bases:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False  # a es testigo de que n es compuesto
    return True


def _pollard_brent(n: int) -> int:
    """Devuelve un divisor no trivial de un compuesto impar n (rho de Pollard, variante de Brent)."""
    while True:
        y, c, m = random.randrange(1, n), random.randrange(1, n), 128
        g = r = q = 1
        while g == 1:
            x = y
            for _ in range(r):
                y = (y * y + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                for _ in range(min(m, r - k)):
                    y = (y * y + c) % n
                    q = q * abs(x - y) % n
                g = gcd(q, n)
                k += m
            r *= 2
        if g == n:  # nos hemos pasado: retrocedemos paso a paso
            g = 1
            while g == 1:
                ys = (ys * ys + c) % n
                g = gcd(abs(x - ys), n)
        if g != n:
            return g


# EJERCICIO 1
def es_primo(n: int) -> bool:
    """ Recibe un entero n y devuelve verdadero si es un número primo y falso en caso contrario.

    Usa división por los primos menores que 1000 y, después, el test de Miller-Rabin.
    Es determinista para n < 3.3 * 10^24; por encima añade 20 bases aleatorias
    (probabilidad de error menor que 4^-20).

    Args:
        n (int): Entero

    Returns:
        true si el entero es un número primo.
        false en caso contrario.

    Raises: None

    Examples:
        es_primo(5)=True
        es_primo(4)=False
    """
    if n < 2:
        return False
    for p in _PRIMOS_PEQUENOS:
        if n % p == 0:
            return n == p
    if n < 1000 * 1000:  # sin divisores primos <= raíz de n
        return True
    bases = _BASES_MR
    if n >= _LIMITE_MR_DETERMINISTA:
        bases = bases + tuple(random.randrange(2, n - 1) for _ in range(_RONDAS_MR_EXTRA))
    return _miller_rabin(n, bases)


# EJERCICIO 2
def lista_primos(a, b) -> List[int]:
    """ Recibe dos enteros a y b y devuelva la lista de números primos en el intervalo [a, b)

    Usa una criba de Eratóstenes segmentada sobre [a, b). Si el intervalo es muy
    estrecho comparado con raíz de b, aplica es_primo a cada impar.

    Args:
        a (int): Elemento inicial del intervalo (incluido)
        b (int): Elemento final del intervalo (no incluido)

    Returns:
        List[int]: lista ordenada de primos mayores o iguales que a y menores que b.

    Raises: None

    Examples:
        lista_primos(1,11)=[2,3,5,7]
    """
    a = max(a, 2)
    if b <= a:
        return []

    limite = isqrt(b - 1)
    if limite > 2 * 10**6 and b - a < limite:
        inicio = a if a % 2 == 1 or a == 2 else a + 1
        primos = [2] if a == 2 else []
        return primos + [k for k in range(max(inicio, 3), b, 2) if es_primo(k)]

    segmento = bytearray([1]) * (b - a)       # segmento[i] representa a + i
    for p in _criba(limite):
        inicio = max(p * p, (a + p - 1) // p * p)   # primer múltiplo de p en [a, b) que no es p
        if inicio < b:
            segmento[inicio - a::p] = bytes(len(range(inicio - a, b - a, p)))
    return [a + i for i in compress(range(b - a), segmento)]


# EJERCICIO 3
def factorizar(n: int) -> Dict[int, int]:
    """ Recibe  un entero n y devuelve un diccionario cuyas claves son los primos que dividen a n y sus valores los
    correspondientes exponentes en la descomposición en producto de factores primos de n.

    Divide primero por los primos menores que 1000 y separa lo que queda con el
    método rho de Pollard (variante de Brent), comprobando cada factor con es_primo.

    Args:
        n (int): Entero que se desea factorizar.

    Returns:
        Dict[int,int]: Diccionario en el que las claves son primos positivos p_i que dividen a n y, para cada p_i,
            su valor asociado es el máximo exponente e_i tal que p_i^(e_i) divide a n. Si n=0, devuelve un diccionario vacío.

    Raises: None

    Examples:
        factorizar(12)={2: 2, 3: 1}
        factorizar(0)={}
    """
    # Teorema fundamental de la aritmética: todo entero se escribe de forma única
    # como producto de potencias de primos.
    if n in (-1, 0, 1):
        return {}
    n = abs(n)
    factores: Dict[int, int] = {}

    # 1. División por tentativa con primos pequeños
    for p in _PRIMOS_PEQUENOS:
        if p * p > n:
            break
        while n % p == 0:
            n //= p
            factores[p] = factores.get(p, 0) + 1

    # 2. Lo que queda no tiene factores menores que 1000: rho de Pollard
    pendientes = [n] if n > 1 else []
    while pendientes:
        m = pendientes.pop()
        if es_primo(m):
            factores[m] = factores.get(m, 0) + 1
            continue
        r = isqrt(m)
        if r * r == m:           # cuadrado perfecto: rho tarda mucho en p^2
            pendientes += [r, r]
            continue
        d = _pollard_brent(m)
        pendientes += [d, m // d]

    return dict(sorted(factores.items()))


# EJERCICIO 4
def mcd(a: int, b: int) -> int:
    """ Calcula el máximo común divisor de dos enteros a y b usando el algoritmo de Euclides.
    Args:
        a (int): Primer entero.
        b (int): Segundo entero.

    Returns:
        int: devuelve el máximo común divisor de a y b

    Raises: None

    Examples:
        mcd(10,15)=5
    """
    # Aseguramos trabajar con valores absolutos
    a, b = abs(a), abs(b)

    # Aplicamos el algoritmo de Euclides
    while b != 0:   # buscamos el último divisor no nulo
        a, b = b, a % b

    return a


def bezout(a: int, b: int) -> Tuple[int, int, int]:
    """ Calcula el máximo común divisor d de dos enteros a y b junto con dos enteros x e y tales que
            d=ax+by

    Algoritmo de Euclides extendido en versión iterativa (la recursiva podía superar el
    límite de recursión de Python con números muy grandes).

    Args:
        a (int): Primer entero.
        b (int): Segundo entero.

    Returns: (d,x,y)
        d (int): Máximo común divisor. d = mcd(a,b)
        x (int): Coeficiente de a.
        y (int): Coeficiente de b.

    Raises: None

    Examples:
        bezout(6,10)=(2,2,-1)
    """
    # Invariantes: r0 = a*x0 + b*y0  y  r1 = a*x1 + b*y1
    r0, r1 = a, b
    x0, x1 = 1, 0
    y0, y1 = 0, 1
    while r1 != 0:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    if r0 < 0:  # el mcd se devuelve siempre positivo
        r0, x0, y0 = -r0, -x0, -y0
    return (r0, x0, y0)


# EJERCICIO 5 (OPCIONAL)
def mcd_n(nlist: List[int]) -> int:
    """ Dados una lista de enteros, devuelve el máximo divisor común a todos ellos.
    Args:
        nList (List[int]): Lista de enteros.

    Returns:
        int: devuelve el máximo entero que divide a todos los enteros de la lista.

    Raises: None

    Examples:
        mcd([4,10,14])=2
    """
    # El mcd es asociativo: basta con aplicarlo de dos en dos.
    if not nlist:
        return 0
    d = abs(nlist[0])
    for num in nlist[1:]:
        d = mcd(d, num)
        if d == 1:      # ya no puede bajar más
            break
    return d


def bezout_n(nlist: List[int]) -> Tuple[int, List[int]]:
    """ Dada una lista de enteros [a_1,...,a_n], devuelve el máximo divisor común d a todos ellos y una
    lista de coeficientes [x_1,...,x_n] tal que
        d=a_1*x_1+...a_n*x_n

    Args:
        nList (List[int]): Lista de enteros.

    Returns: (d,X)
        d (int): Máximo entero que divide a todos los enteros de la lista.
        X (List[int]): Lista de coeficientes [x_1,...,x_n].

    Raises: None

    Examples
        bezout_n([4,10,14])=(2,[-2,1,0])
    """
    if not nlist:
        return (0, [])

    # d = a_1*x_1 + ... + a_i*x_i se mantiene en cada paso
    d = abs(nlist[0])
    coef = [1 if nlist[0] >= 0 else -1] + [0] * (len(nlist) - 1)
    for i in range(1, len(nlist)):
        if nlist[i] == 0:           # un 0 no cambia el mcd
            continue
        d, x, y = bezout(d, nlist[i])
        coef = [c * x for c in coef]   # los coeficientes anteriores se multiplican por x
        coef[i] = y
    return (d, coef)


# EJERCICIO 6
def coprimos(a: int, b: int) -> bool:
    """ Determina si dos enteros son coprimos.
    Args:
        a (int): Primer entero.
        b (int): Segundo entero.

    Returns:
        bool: Verdadero si son coprimos y falso si no.

    Raises: None

    Examples:
        coprimos(14,20)=False
        coprimos(14,15)=True
    """
    return mcd(a, b) == 1


# EJERCICIO 7
def potencia_mod_p(base: int, exp: int, p: int) -> int:
    """ Calcula potencias módulo p.

    Args:
        base (int): Base de la potencia.
        exp (int): Exponente al que se eleva la base.
        p (int): Módulo.

    Returns:
        int: Resto de dividir base^exp módulo p.

    Raises:
        ZeroDivisionError: Si el módulo es 0, si la base y el exponente son ambos 0
        o si el exponente es negativo y la base no es invertible módulo p.

    Examples:
        potencia_mod_p(2,3,7)=1
    """
    # Podemos aprovechar que (a*b) mod p = ((a mod p)*(b mod p)) mod p
    if p == 0:
        raise ZeroDivisionError("El módulo no puede ser 0")
    if base == 0 and exp == 0:
        raise ZeroDivisionError("0^0 no está definido")
    p = abs(p)

    base = base % p  # da igual usar la base o su resto

    # Exponente negativo: a^(-k) = (a^(-1))^k
    if exp < 0:
        base = inversa_mod_p(base, p)
        exp = -exp

    # Exponenciación rápida (binaria)
    resultado = 1
    while exp > 0:
        if exp % 2 == 1:        # si el bit actual del exponente es 1
            resultado = (resultado * base) % p
        base = (base * base) % p
        exp //= 2
    return resultado % p        # % p para el caso p = 1


# EJERCICIO 8
def inversa_mod_p(n: int, p: int) -> int:
    """ Calcula la inversa de un número n módulo p.

    Args:
        n (int): Número que se desea invertir
        p (int): Módulo.

    Returns:
        int: Entero x entre 0 y p-1 tal que n*x es congruente con 1 módulo p.

    Raises:
        ZeroDivisionError: Si el módulo es 0 o si n no es invertible módulo p.

    Examples:
        inversa_mod_p(2,7)=4
    """
    if p == 0:
        raise ZeroDivisionError("El módulo no puede ser 0")
    p = abs(p)
    d, x, _ = bezout(n, p)
    if d != 1:
        raise ZeroDivisionError(f"No existe inversa de {n} módulo {p}, no son coprimos")
    return x % p


# EJERCICIO 9
def euler(n: int) -> int:
    """ Calcula la función phi de Euler de un entero positivo n, es decir, cuenta cúantos enteros positivos
    menores que n son coprimos con n.

    Args:
        n (int): Número entero positivo.

    Returns:
        int: Función phi de Euler de n (0 si n <= 0).

    Raises: None

    Examples:
        euler(7)=6
        euler(15)=8
    """
    if n <= 0:
        return 0
    # Fórmula multiplicativa: phi(n) = n * prod(1 - 1/p)
    resultado = n
    for primo in factorizar(n):
        resultado = resultado // primo * (primo - 1)
    return resultado


# EJERCICIO 10
def legendre(n: int, p: int) -> int:
    """ Dado un entero n y un número primo p, calcula el símbolo de Legendre de n módulo p.

    Args:
        n (int): Número entero.
        p (int): Número primo impar.

    Returns:
        int: Símbolo de Legendre de Euler de n módulo p:
            0 si es múltiplo de p
            1 si es un cuadrado perfecto (distinto de 0), módulo p
            -1 en caso contrario.

    Raises:
        ZeroDivisionError: Si el módulo p es 0.
        ValueError: Si p = 2 o se detecta que p no es primo.

    Examples:
        legendre(2,5)=-1
        legendre(2,7)=1
        legendre(10,5)=0
    """
    if p == 0:
        raise ZeroDivisionError("El módulo no puede ser 0")
    p = abs(p)
    if p == 2:
        raise ValueError("El símbolo de Legendre requiere un primo impar p >= 3")

    n = n % p
    if n == 0:
        return 0

    # Criterio de Euler: n^((p-1)/2) = (n/p) (mod p)
    r = potencia_mod_p(n, (p - 1) // 2, p)
    if r == 1:
        return 1
    if r == p - 1:              # equivale a -1 mod p
        return -1
    raise ValueError(f"{p} no es primo")


# EJERCICIO 11 y 12 (OPCIONAL: módulos no coprimos)
def resolver_sistema_congruencias(alist: List[int], blist: List[int], plist: List[int]) -> Tuple[int, int]:
    """ Dadas tres listas de números enteros [a_1,...,a_n], [b_1,...,b_n] y [p_1,...,p_n], resuelve el sistema de congruencias

    a_i * x = b_i (mod p_i)   i=1,...,n

    devolviendo un entero r y un módulo m tales que las soluciones del sistema corresponden a todos los enteros
    x congruentes con r módulo m. Los módulos no tienen por qué ser coprimos dos a dos.

    Args:
        alist (List[int]): Lista de coeficientes de la variable x, [a_1,...,a_n].
        blist (List[int]): Lista de términos independientes [b_1,...,b_n].
        plist (List[int]): Lista de módulos [p_1,...,p_n]

    Returns: (r,m)
        r (int): Entero entre 0 y m-1.
        m (int): Entero positivo, módulo de la solución.

    Raises:
        IncompatibleEquationError: Si no es posible resolver el sistema.
        ValueError: Si las listas están vacías, tienen distinta longitud o algún módulo es 0.

    Examples:
        resolverSistema([2;3;5])=(4,5)
        resolverSistema([2;4;6])=(2,3)
        resolverSistema([1;1;3],[4;7;11])=(10,33)
    """
    if not (len(alist) == len(blist) == len(plist)):
        raise ValueError("Las listas introducidas deben ser de la misma longitud")
    if not alist:
        raise ValueError("El sistema debe tener al menos una ecuación")

    r, m = 0, 1     # al principio, cualquier x es solución: x = 0 (mod 1)
    for a, b, p in zip(alist, blist, plist):
        if p == 0:
            raise ValueError("Los módulos no pueden ser 0")
        p = abs(p)

        # 1. a x = b (mod p) tiene solución si y solo si d = mcd(a, p) divide a b.
        #    En ese caso equivale a x = (b/d) * (a/d)^(-1) (mod p/d).
        d = mcd(a, p)
        if b % d != 0:
            raise IncompatibleEquationError(f"{a}x = {b} (mod {p}) no tiene solución")
        p_i = p // d
        r_i = (b // d) * inversa_mod_p(a // d, p_i) % p_i

        # 2. Combinamos x = r (mod m) con x = r_i (mod p_i) (teorema chino generalizado):
        #    hay solución si y solo si g = mcd(m, p_i) divide a r_i - r, y es única módulo mcm(m, p_i).
        g, s, _ = bezout(m, p_i)
        if (r_i - r) % g != 0:
            raise IncompatibleEquationError("Las congruencias del sistema son incompatibles")
        mcm = m // g * p_i
        r = (r + m * ((r_i - r) // g * s % (p_i // g))) % mcm
        m = mcm

    return (r, m)


# EJERCICIO 13 (OPCIONAL)
def raiz_mod_p(n: int, p: int) -> int:
    """ Encuentra, si existe, una raíz cuadrada para un entero n módulo un número primo p.

    Usa la fórmula directa n^((p+1)/4) si p = 3 (mod 4) y el algoritmo de Cipolla en otro caso.
    La otra raíz es p - x.

    Args:
        n (int): Entero del que se desea hallar la raíz.
        p (int): Módulo. Se asume que es un número primo.

    Returns:
        int: Entero x entre 0 y p-1 tal que x^2 = n (mod p).

    Raises:
        NotQuadraticResidueError (subclase de IncompatibleEquationError): Si n no tiene raíz módulo p.
        ZeroDivisionError: Si p = 0.
        ValueError: Si se detecta que p no es primo.

    Examples:
        raiz_mod_p(2,7)=3
    """
    if p == 0:
        raise ZeroDivisionError("El módulo no puede ser 0")
    p = abs(p)
    n %= p
    if p == 2 or n == 0:
        return n
    if legendre(n, p) != 1:
        raise NotQuadraticResidueError(f"{n} no es un cuadrado módulo {p}")

    if p % 4 == 3:
        x = potencia_mod_p(n, (p + 1) // 4, p)
    else:
        # Cipolla: buscamos t tal que w = t^2 - n no sea un cuadrado módulo p.
        # En el cuerpo F_p(raíz de w), (t + raíz de w)^((p+1)/2) es una raíz de n.
        t = 1
        while legendre(t * t - n, p) != -1:
            t += 1
        w = (t * t - n) % p

        def mult(u, v):  # (u0 + u1*raíz(w)) * (v0 + v1*raíz(w))
            return ((u[0] * v[0] + u[1] * v[1] * w) % p, (u[0] * v[1] + u[1] * v[0]) % p)

        resultado, base, e = (1, 0), (t, 1), (p + 1) // 2
        while e > 0:
            if e % 2 == 1:
                resultado = mult(resultado, base)
            base = mult(base, base)
            e //= 2
        x = resultado[0]

    if x * x % p != n:
        raise ValueError(f"{p} no es primo")
    return x


# EJERCICIO 14 (OPCIONAL)
def ecuacion_cuadratica(a: int, b: int, c: int, p: int) -> Tuple[int, int]:
    """ Halla, si es posible, las dos posibles soluciones de la ecuación cuadrática ax^2+bx+c=0 (mod p).
    Devuelve una tupla con las dos raíces (distintas o una misma raíz repetida en caso de ser doble).

    Usa la fórmula x = (-b ± raíz(b^2 - 4ac)) / (2a), con las operaciones módulo p.

    Args:
        a (int): Coeficiente de x^2.
        b (int): Coeficiente de x.
        c (int): Término independiente.
        p (int): Módulo. Se asume que es un número primo.

    Returns: (x1,x2)
        x1 (int): Primera solución. Entero entre 0 y p-1.
        x2 (int): Segunda solución. Entero entre 0 y p-1 (x1 <= x2).

    Raises:
        IncompatibleEquationError: Si no es posible resolver la ecuación.
        ZeroDivisionError: Si p = 0.

    Examples:
        ecuacion_cuadratica(4,1,3,11)
        ecuacion_cuadratica(4,1,5,11)=(3, 5)
        ecuacion_cuadratica(1,2,1,11)=(10,10)
    """
    if p == 0:
        raise ZeroDivisionError("El módulo no puede ser 0")
    p = abs(p)
    a, b, c = a % p, b % p, c % p

    if p == 2:  # 2a no es invertible: probamos x = 0 y x = 1
        soluciones = [x for x in (0, 1) if (a * x * x + b * x + c) % 2 == 0]
        if not soluciones:
            raise IncompatibleEquationError(f"La ecuación no tiene solución módulo {p}")
        return (soluciones[0], soluciones[-1])

    if a == 0:
        raise IncompatibleEquationError(f"a = 0 (mod {p}): la ecuación no es cuadrática")

    discriminante = (b * b - 4 * a * c) % p
    r = raiz_mod_p(discriminante, p)          # lanza NotQuadraticResidueError si no hay raíz
    inv_2a = inversa_mod_p(2 * a, p)
    x1 = (-b + r) * inv_2a % p
    x2 = (-b - r) * inv_2a % p
    return (min(x1, x2), max(x1, x2))
