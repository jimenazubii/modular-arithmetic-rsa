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
"""

from typing import Tuple, List, Dict
from excepciones import IncompatibleEquationError


# EJERCICIO 1
def es_primo(n:int)->bool:
    """ Recibe un entero n y devuelve verdadero si es un número primo y falso en caso contrario.

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

    # Documentación y teoremas utilizados:
    #   - Teorema de la cota para divisores primos. 

    # Caso 1: Los números menores o iguales a 1 no son primos
    if n <= 1:
        return False
    
    # Caso 2: 2 es primo (el único par que lo es)
    elif n == 2:
        return True
    
    # Caso 3: cualquier número par mayor que 2 no es primo
    elif n % 2 == 0:
        return False
    
    # Caso 4: Recorremos divisores desde 3 hasta la raíz cuadrada de n
    for i in range(3, int(n**0.5)+1, 2):    # Salto de 2 en dos porque ya he descartado los pares
        if n % i == 0:
            return False
        
    return True

# EJERCICIO 2
def lista_primos(a,b)-> List[int]:
    """ Recibe dos enteros a y b y devuelva la lista de números primos en el intervalo [a, b)

    Args:
        a (int): Elemento inicial del intervalo (incluido)
        b (int): Elemento final del intervalo (no incluido)
    
    Returns:
        List[int]: lista ordenada de primos mayores o iguales que a y menores que b.

    Raises: None
    
    Examples:
        lista_primos(1,11)=[2,3,5,7]
    """
    lista_primos = []
    for i in range(a,b):            # recorro todos los enteros desde a hasta b-1
        if es_primo(i):             # uso la función anterior
            lista_primos.append(i)  # si es primo lo guardo en la lista
    return lista_primos


# EJERCICIO 3
def factorizar(n:int)->Dict[int,int]:
    """ Recibe  un entero n y devuelve un diccionario cuyas claves son los primos que dividen a n y sus valores los
    correspondientes exponentes en la descomposición en producto de factores primos de n.
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
    # Utilizamos el teorema fundamental de la aritmética: todo número entero se puede
    # escribir de manera única como producto de potencias de primos.

    # Por tanto, factorizar significa descomponer un número en sus factores
    # primos y contar las veces que aparece cada uno.
    
    # Casos especiales: n = -1, 0, 1 → devolver {}
    if n in (-1,0,1):
        return {}
    
    n = abs(n)

    # 3. Crear diccionario vacío para guardar la factorización
    dic_factores = {}

    # 4. Contar factores de 2:
    contador = 0
    while n % 2 == 0:
        n //= 2
        contador += 1
    if contador > 0:
        dic_factores[2] = contador

    # Comprobamos divisores inmpares desde 3 hasta la raíz cuadrada de n
    divisor = 3
    while divisor**2 <= n:
        contador = 0
        while n % divisor == 0:
            n //= divisor
            contador += 1
        if contador > 0:
            dic_factores[divisor] = contador
        divisor += 2    # Solo impares

    # Si al final n es mayor que 1, es un primo
    if n > 1:
        dic_factores[n] = 1

    return dic_factores

# EJERCICIO 4
def mcd(a:int,b:int)->int:
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


def bezout(a:int, b:int) -> Tuple[int,int,int]:
    """ Calcula el máximo común divisor d de dos enteros a y b junto con dos enteros x e y tales que
            d=ax+by

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
    # Caso base: si b=0, el mcd es a, y los coeficietes son (1,0)
    if b == 0:
        return (abs(a), 1 if a > 0 else -1, 0)
    
    # Paso recursivo: llamamos con (b, a mod b)
    d, x1, y1 = bezout(b, a%b)

    # Reconstruimos coeficientes usando la identidad: d = b*x1 + (a mod b)*y1
    # pero (a mod b) = a - (a//b)*b y así conseguimos nuevas x,y
    x = y1                      # Nuevo coef para "a" es el anterior y1.
    y = x1 - (a // b)*y1        # Nuevo coef para"b" se ajusta con la división entera.

    return (d, x, y)            # Devolvemos (mcd, coef de a, coef de b)

# EJERCICIO 5 (OPCIONAL)
def mcd_n(nlist:List[int])->int:
    """ Dados una lista de enteros, devuelve el máximo divisor común a todos ellos.
    Args:
        nList (List[int]): Lista de enteros.        
    
    Returns:
        int: devuelve el máximo entero que divide a todos los enteros de la lista.

    Raises: None

    Examples:
        mcd([4,10,14])=2
    """
    # Para calcular el mcd de muchos números basta con ir aplicando el mcd de 2 en 2. --> Es asociativo

    # Caso especial: lista vacía --> no tiene sentido, devolvemos 0
    if not nlist:
        return 0
    
    # Inicializamos con el primer elemento
    d = abs(nlist[0])

    # Recorremos el resto de la lista
    for num in nlist[1:]:
        # Aplicamos Euclides 
        a, b= d, abs(num)
        while b != 0:
            a, b = b, a%b
        d=a

    return d


def bezout_n(nlist:List[int])->Tuple[int,List[int]]:
    
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
    # Caso especial: lista vacía
    if not nlist:
        return (0, [])
    
    # Inicializamos con el primer elemento como mcd
    d = abs(nlist[0])
    coef = [1] + [0]*(len(nlist)-1) # Solo el primero tiene coef=1, el resto 0

    # Vamos incorporando el resto
    for i in range(1, len(nlist)):
        a = d
        b = abs(nlist[i])

        # Algoritmo extendido de Euclides para (a,b)
        if b == 0:                  # Si el nuevo número es 0, no aporta nada al mcd
            continue
        d_temp, x, y = bezout(a,b)  # Usamos la versión extendida de Euclides en (a,b)

        # Ajustamos coeficientes acumulados
        coef = [c*x for c in coef]  # Multiplicamos los anteriores por x
        coef[i] = y                 # Nuevo coef para ai
        d = d_temp                  # Actualizamos el mcd con el obtenido
    return (d, coef)

# EJERCICIO 6
def coprimos(a:int,b:int)->bool:
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
    if mcd(a,b) == 1:
        return True
    return False

# EJERCICIO 7
def potencia_mod_p(base:int, exp:int, p:int) -> int:
    """ Calcula potencias módulo p.

    Args:
        base (int): Base de la potencia.
        exp (int): Exponente al que se eleva la base.
        p (int): Módulo.
    
    Returns:
        int: Resto de dividir base^exp módulo p.

    Raises:
        ZeroDivisionError: Si el módulo es 0 o si la base y el exponente
        son ambos 0 al mismo tiempo.

    Examples:
        potencia_mod_p(2,3,7)=1
    """
    # Podemos aprovechar que (a*b) mod p = ((a mod p)*(b mod p)) mod p

    # Evitamos que pete el programa dividiendo entre 0
    if p == 0 or base == 0 or exp == 0:
        raise ZeroDivisionError("El módulo no puede ser 0")
    
    base = base % p # Reducimos la base al principio --> da igual usar una base o su resto

    # Caso exponente negativo --> usamos la inversa modular
    if exp < 0:
        inv = inversa_mod_p(base, p)         # Reutilizamos la función inversa
        return potencia_mod_p(inv, -exp, p)  # Ahora que lo tenemos elevado a -1 podemos poner el exponente como positivo
    
    # Método de exponenciación rápida / binaria
    resultado = 1
    while exp > 0:
        if exp % 2 == 1:        # Si el exponente es impar, multiplicamos el resultado por la base
            resultado = (resultado * base) % p
        base = (base**2)%p      # Siempre elevamos la base al cuadrado
        exp //= 2               # Reducimos el exponente a la mitad
    return resultado            # Cuando el exponente llega a 0, el resultado ya contiene toda la solución

# EJERCICIO 8
def inversa_mod_p(n:int,p:int)->int:
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
    
    d, x, _ = bezout(n, p)

    if d != 1:
        raise ZeroDivisionError(f"No existe inversa de {n} módulo {p}, no son coprimos")
    
    return x%p

# EJERCICIO 9
def euler(n:int)->int:
    """ Calcula la función phi de Euler de un entero positivo n, es decir, cuenta cúantos enteros positivos
    menores que n son coprimos con n.

    Args:
        n (int): Número entero positivo.
    
    Returns:
        int: Función phi de Euler de n.

    Raises: None

    Examples:
        euler(7)=6
        euler(15)=8
    """
    if n <= 0:
        return 0
    
    if es_primo(n):
        return n-1
    
    # Factorizamos n para aplicar la fórmula
    factores = factorizar(n)

    # Fórmula multiplicativa 
    resultado = n
    for primo in factores.keys():
        resultado = resultado // primo * (primo - 1)

    return resultado

# EJERCICIO 10
def legendre(n:int,p:int)->int:
    """ Dado un entero n y un número primo p, calcula el símbolo de Legendre de n módulo p.

    Args:
        n (int): Número entero.
        p (int): Número primo.
    
    Returns:
        int: Símbolo de Legendre de Euler de n módulo p:
            0 si es múltiplo de p
            1 si es un cuadrado perfecto (distinto de 0), módulo p
            -1 en caso contrario.

    Raises:
        ZeroDivisionError: Si el módulo p es 0.

    Examples:
        legendre(2,5)=-1
        legendre(2,7)=1
        legendre(10,5)=0
    """
    # Los pasos para realizarlo serían:
        # Reducir n mod p
        # Si n == 0 --> devolver 0
        # Calcular r = n^((p-1)/2) mod p con el método de exponenciación rápida
        # Si r == 1 --> devolver 1
        # Si r === p-1 --> devolver -1
    if p == 0:
        raise ZeroDivisionError("El módulo no puede ser 0")
    
    if p == 2:
        raise ValueError("El símbolo de Legendre requiere ser primo impar p>=3")
    
    n = n % p                       # Reducimos n módulo p

    if n == 0:
        return 0                    # Caso múltiplo de p
    
    # Aplicamos el criterio de Euler: n^((p-1)//2) mod p
    exp = (p-1)//2
    r = potencia_mod_p(n, exp, p)

    if r == 1:
        return 1
    elif r == p - 1:                # Equyivalente a -1 mod p
        return -1
    else:
        raise ValueError("Resultado inexistente: p puede no ser primo")


# EJERCICIO 11
def resolver_sistema_congruencias(alist:List[int],blist:List[int],plist:List[int])->Tuple[int,int]:
    """ Dadas tres listas de números enteros [a_1,...,a_n], [b_1,...,b_n] y [p_1,...,p_n], resuelve el sistema de congruencias
    
    a_i * x = b_i (mod p_i)   i=1,...,n
    
    devolviendo un entero r y un módulo m tales que las soluciones del sistema corresponden a todos los enteros
    x congruentes con r módulo m.

    Args:
        alist (List[int]): Lista de coeficientes de la variable x, [a_1,...,a_n].
        blist (List[int]): Lista de términos independientes [b_1,...,b_n].
        plist (List[int]): Lista de módulos [p_1,...,p_n]
    
    Returns: (r,m)
        r (int): Entero entre 0 y m-1.
        m (int): Entero positivo, módulo de la solución.

    Raises:
        IncompatibleEquationError: Si no es posible resolver el sistema.

    Examples:
        resolverSistema([2;3;5])=(4,5)
        resolverSistema([2;4;6])=(2,3)
        resolverSistema([1;1;3],[4;7;11])=(10,33)        
    """

    # 1. Comprobar que todas las listas tienen la misma longitud
    if len(alist) != len(blist) or len(blist) != len(plist):
        raise ValueError("Las listas introducidas deben ser de la misma longitud")
    
    x0 = 0 # acumulador de la soluciónn
    m = 1  # producto de todos los módulos
    
    # 2. Calcular el producto de todos los módulos
    for p in plist:
        m *= p
    
    # 3. Para cada congruencia:
    for a, b, p in zip(alist, blist, plist): # zip coge un elemento de cada lista en para crear una tupla de lsitas nuevas y poder iterar sobre las tres listas iniciales a la vez
        try:
            inv_a = inversa_mod_p(a, p)         # calcula la inversa modular
            x_i = (b * inv_a) % p               # pasar a la ecuación de forma más simple
            n = m // p                          # calcular Ni
            inv_n = inversa_mod_p(n, p)         # calcular la inversa modular de Ni --> estos valores sirven para aplicar la fórmula de Tma chino del resto
            x0 = (x0 + x_i * inv_n * n) % m     # acumular la suma y reducirlo a módulo m
        except Exception:
            raise IncompatibleEquationError 

    return (x0, m)

# EJERCICIO 13 (OPCIONAL)
def raiz_mod_p(n:int,p:int)->int:
    """ Encuentra, si existe, una raíz cuadrada para un entero n módulo un número primo p.

    Args:
        n (int): Entero del que se desea hallar la raíz.
        p (int): Módulo. Se asume que es un número primo.
    
    Returns:
        int: Entero x entre 0 y p-1 tal que x^2 = n (mod p).

    Raises:
        IncompatibleEquationError: Si no es posible hallar dicha raíz.

    Examples:
        raiz_mod_p(2,7)=3
    """
    #Opcional
    pass


# EJERCICIO 14 (OPCIONAL)
def ecuacion_cuadratica(a:int,b:int,c:int,p:int)->Tuple[int,int]:
    """ Halla, si es posible, las dos posibles soluciones de la ecuación cuadrática ax^2+bx+c=0 (mod p).
    Devuelve una tupla con las dos raíces (distintas o una misma raíz repetida en caso de ser doble).

    Args:
        a (int): Coeficiente de x^2.
        b (int): Coeficiente de x.
        c (int): Término independiente.
        p (int): Módulo. Se asume que es un número primo.
    
    Returns: (x1,x2)
        x1 (int): Primera solución. Entero entre 0 y p-1.
        x2 (int): Segunda solución. Entero entre 0 y p-1.

    Raises:
        IncompatibleEquationError: Si no es posible resolver la ecuación.

    Examples:
        ecuacion_cuadratica(4,1,3,11)
        ecuacion_cuadratica(4,1,5,11)=(3, 5)
        ecuacion_cuadratica(1,2,1,11)=(10,10)
    """
    #Opcional
    pass