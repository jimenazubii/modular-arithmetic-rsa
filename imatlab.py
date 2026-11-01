"""
imatlab.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP15B
Integrantes:
    - Pilar Perez Hernández 
    - Jimena Zubizarreta Gómez 

Descripción:
Sistema interactivo IMAT-LAB de resolución de ecuaciones en aritmética modular.

Interfaz de acceso interactivo o por lotes a la librería modular.py. Si este script se ejecuta sin parámetros,
lanzará la interfaz de usuario para el modo interactivo.
"""

from typing import TextIO
from io import StringIO
import sys 
import re 
from excepciones import NE, NOP, IncompatibleEquationError
import modular as f 


patron_general = re.compile(
    r"^\s*"                     #marca el principio de una linea, deja que pueda haber espacios antes 
    r"([A-Za-z_]\w*)"           #nombre de la funcion: puede empezar por una letra o un "_" y puede seguir con \w (sigue con letras, digitos o "_")
    r"\s*\(\s*(.*?)\s*"         #detectar los paréntesis y los argumentos que mete el usuario o los ficheros
    r"\)\s*$"                   #cierra la expresión y deja que haya espacios al final 
)
regex_particular = re.compile(
    r"^\s*"                                                #marca el principio de una linea, deja que pueda haber espacios antes
    r"(\[\s*-?\d+\s*;\s*-?\d+\s*;\s*-?\d+\s*\]"            # detecta los paréntesis y empieza a detectar el primer bloque de datos. 
    r"(?:\s*,\s*\[\s*-?\d+\s*;\s*-?\d+\s*;\s*-?\d+\s*\])*)" #detecta si hay 0 o más después del ya detectado
    r"\s*$"                                                 # cierra la expresión y deja que haya espacios al final 
)


def detectar_funcion(linea:str): 
    """
    Devuelve (funcion, argumentos) o lanza NOP si no encaja 
    """
    linea = linea.strip()                                   #limpia la linea de posibles espacios al principio y al final 
    if not linea: 
        raise NOP("La línea esta vacía")                    #si la línea está vacía salta el error 
    m = patron_general.match(linea)                         #compara lo que se ha metido por argumento con el el patron de regex
    if not m: 
        raise NOP("El formato de la llamada no es válido")  #si no hay un match, lanza un error 
    
    funcion = m.group(1)                                    # en el match, el primer grupo será la función a realizar 
    argumentos = m.group(2)                                 # en el match, el segundo grupo será los argumentos (los numeros) necesarios para ejecutar la función 
    return funcion, argumentos 

def formatear_argumentos(funcion:str, argumentos:str): 
    """
    En todas las funciones menos resolverSistema formatea los argumentos
        - separa por comas 
        - convierte a int/float
    Lanza excepciones: 
        - NOP si hay fallos de formato 
        - NE si no existe 
    """
    m = re.match(regex_particular, argumentos)               #compara lo que se ha metido por argumento con el el patrón regex especial de la función resolverSistema
    if m:
        cadenas = m.group(1) 
        listas = [s.strip() for s in cadenas.replace('[','').replace(']','').split(',') if s.strip()]   #quita los corchetes y divide por comas para separar por bloques 
        alist, blist, plist = [], [], []
        for lista in listas:
            elementos = [e.strip() for e in lista.split(';') if e.strip()]      #para cada bloque que hemos separado, separa cada elemento por ;
            if len(elementos) != 3:
                raise NOP("[resolverSistema] Cada bloque debe ser [a;b;p].")    #lanza un error si el número de elementos no es el necesario 
            a, b, p = map(int, elementos)                                       #convierte los strings a enteros para poder operar con ellos 
            alist.append(a); blist.append(b); plist.append(p)
        return (alist, blist, plist)   
    if argumentos == "":                                     #si no hay argumentos, devuelve una lista vacía 
        return []
    numeros = [] 
    try:                                             #si no hay un match con resolver sistema, tenemos que formatear los argumentos para el resto de funciones 
        for x in argumentos.strip("[").strip("]").split(","):    #si tiene corchetes (caso de las listas) se aplica la función strip() y se dividen los elementos por comas
            numeros.append(int(x.strip()))                       #convierte cada elemento a un int y lo guarda en una lista para que lo puedan leer las funciones de modular 
        return numeros
    except ValueError: 
        raise NOP("Debes meter un número entero")


def error_formato(func_name, esperado, dados, args_obj) -> str: #creamos una función para que sea capaz de dar mensajes de error èrsonalizados 
    """
    Lanza una excepción NOP con un mensaje estándar para cada función que lo necesite
    """
    raise NOP(                                                  #lanza la excepción NOP
        f"[{func_name}] número de argumentos incorrecto: "      
        f"se esperaban {esperado}, pero se recibieron {dados}. "
        f"Argumentos recibidos: {args_obj!r}"
    )

def h_primo(args):
    """
    Espera un argumento entero y llama a la función de modular con ese argumento 
    Al llamar a la función de modular devolverá True/False 

    Excepciones: lanza NOP (con el formato de error_formato) si el número de argumentos no corresponde con el esperado
    """
    if len(args) != 1:
        error_formato("primo", "1 argumento", len(args), args)
    return f.es_primo(args[0])

def h_primos(args):
    """
    Espera dos argumentos enteros y llama a la función del modular con estos argumentos. 
    Al llamar a la función del modular devolverá una lista de números en el intervalo
    
    Excepciones: lanza NOP (con el formato de error_formato) si el número de argumentos no corresponde con el esperado
    """
    if len(args) != 2:
        error_formato("primos", "2 argumentos (a,b)", len(args), args)
    return f.lista_primos(args[0], args[1])

def h_factorizar(args):
    """
    Espera un argumento entero y llama a la función de modular con ese argumento 
    Al llamar a la función del modular devolverá un diccionario con los factores como claves y el número de veces que aparecen como valores 
    Caso especial (enunciado): para n en {-1, 0, 1} devuelve el propio n, no un diccionario vacío como hace la función modular

    Excepciones: lanza NOP (con el formato de error_formato) si el número de argumentos no corresponde con el esperado
    """
    if len(args) != 1:
        error_formato("factorizar", "1 argumento (n)", len(args), args)
    n = args[0]
    if n in (-1, 0, 1):
        return n
    return f.factorizar(n) 

def h_mcd(args):
    """
    Si recibe un argumento, devuelve su mismo valor 
    Si recibe dos argumentos, llama a la función de modular (mcd) y devolverá un número entero 
    Si recibe más de dos argumentos, llama a la función del modular (mcd_n) y devolverá un número entero 

    Excepciones: lanza NOP (con el formato de error_formato) si el número de argumentos no corresponde con el esperado (en este caso, solo 0)
    """
    if len(args) == 2: 
        return f.mcd(args[0], args[1])
    elif len(args) == 1: 
        return abs(args[0])
    elif len(args) > 2: 
        return f.mcd_n(args)
    else:
        error_formato("mcd", "2 argumentos (a,b)", len(args), args)

def h_coprimos(args):
    """
    Espera dos argumentos y llama a la función del modular que devolverá True/False 

    Excepciones: lanza NOP (con el formato de error_formato) si el número de argumentos no corresponde con el esperado (en este caso, solo 0)
    """
    if len(args) != 2:
        error_formato("coprimos", "2 argumentos (a,b)", len(args), args)
    return f.coprimos(args[0], args[1])

def h_bezout(args):
    """
    Espera dos argumentos enteros y llama a la función del modular que devolverá el mcd, el coeficiente de a y el coeficiente de b
    
    Excepciones: lanza NOP (con el formato de error_formato) si el número de argumentos no corresponde con el esperado (en este caso, solo 0)
    """
    if len(args) != 2:
        error_formato("bezout", "2 argumentos (a,b)", len(args), args)
    return f.bezout(args[0], args[1])

def h_pow(args):
    """
    Espera 3 argumentos: (base, exp y potencia) y llama a la función del modular que devoolverá base**exp (mod p)
    
    Excepciones: lanza NOP (con el formato de error_formato) si el número de argumentos no corresponde con el esperado (en este caso, solo 0)
    """
    if len(args) != 3:
        error_formato("pow", "3 argumentos (base,exp,p)", len(args), args)
    base, exp, p = args
    if p == 0:                          #Error personalizado por si se intenta que el módulo sea 0
        raise NE("p no puede ser 0")
    try: 
        return f.potencia_mod_p(base, exp, p)
    except ZeroDivisionError as e:      #0^0, o exponente negativo con una base no invertible 
        raise NE(f"No se puede hacer la potencia ({e})")

def h_inv(args):
    """
    Espera 2 argumentos enteros (n,p) y llama a la función del modular que devolverá la inversa de n módulo p

    Excepciones: lanza NOP (con el formato de error_formato) si el número de argumentos no corresponde con el esperado (en este caso, solo 0)
    """
    if len(args) != 2:
        error_formato("inv", "2 argumentos (n,p)", len(args), args)
    n, p = args
    if p == 0:                      #Error personalizado por si se intenta que el módulo sea 0
        raise NE("p no puede ser 0")
    try: 
        return f.inversa_mod_p(n, p)
    except ZeroDivisionError:       #Se lanza un error si no existe la inversa 
        raise NE("no existe inversa")

def h_euler(args):
    """
    Espera un argumento entero n y llama a la función del modular que devolverá un número entero

    Excepciones: lanza NOP (con el formato de error_formato) si el número de argumentos no corresponde con el esperado (en este caso, solo 0)
    """
    if len(args) != 1:
        error_formato("euler", "1 argumento", len(args), args)
    return f.euler(args[0])

def h_legendre(args):
    """
    Espera 2 argumentos entero (n,p) y llama a la función del modular que devolverá: 
        - 0 si p|n 
        - 1 si n es residuo cuadrático mod p 
        - -1 en caso contrario 

    Excepciones: lanza NOP (con el formato de error_formato) si el número de argumentos no corresponde con el esperado (en este caso, solo 0)
    """
    if len(args) != 2:
        error_formato("legendre", "2 argumentos (n,p)", len(args), args)
    n, p = args
    if p == 0:                  #Error personalizado porque p no puede ser 0 
        raise NE("p no puede ser 0")
    try:
        return f.legendre(n, p)
    except ValueError as e:     #p = 2 o p no es primo 
        raise NE(str(e))


def h_resolverSistema(args):
    """
    Espera 3 argumentos, que deben de ser listas de la misma longitud
    Llama a la función del modular que devolverá una tupla de números enteros 

    Excepciones: lanza NOP (con el formato de error_formato) si el número de argumentos no corresponde con el esperado (en este caso, solo 0)
                 lanza NOP si las listas no tienen la misma longitud 
                 lanza NE si hay un IncompatibleEquationError
    """
    if len(args) != 3:
        error_formato("resolverSistema", "tres listas (alist, blist, plist)", len(args), args)
    alist, blist, plist = args
    if not (len(alist) == len(blist) == len(plist) and len(alist) > 0):
        raise NOP("[resolverSistema] Mismo nº de a,b,p y al menos uno.")

    try:
        r, m = f.resolver_sistema_congruencias(alist, blist, plist)
    except IncompatibleEquationError:   #si el sistema no tiene solución
        raise NE("Sistema incompatible")
    except ValueError as e:             #algún módulo es 0
        raise NOP(f"[resolverSistema] {e}")

    return (r % m, m)

def h_mcd_n(args):
    """
    Espera al menos 2 argumentos y llama a la función del modular que devolverá un número entero

    Excepciones: lanza NOP (con el formato de error_formato) si el número de argumentos no corresponde con el esperado (en este caso, solo 0)
    """
    if len(args) < 2:
        error_formato("mcd_n", "lista con al menos 2 enteros", len(args), args)
    return f.mcd_n(args)

def h_bezout_n(args):
    """
    Espera al menos 2 argumentos y llama a la función del modular que devolverá una tupla de enteros (d, coeficiente)
    
    Excepciones: lanza NOP (con el formato de error_formato) si el número de argumentos no corresponde con el esperado (en este caso, solo 0)
    """
    if len(args) < 2:
        error_formato("bezout_n", "lista con al menos 2 enteros", len(args), args)
    return f.bezout_n(args)

def h_raiz(args):
    """
    Espera 2 argumentos enteros (n,p), con p primo, y devuelve la lista ordenada de raíces de n módulo p:
        - [x1, x2] con x1 < x2 si hay dos raíces distintas
        - [x] si solo hay una (n = 0 mod p, o p = 2)

    Excepciones: lanza NOP si el número de argumentos no es 2 y NE si n no tiene raíces módulo p
    """
    if len(args) != 2:
        error_formato("raiz", "2 argumentos (n,p)", len(args), args)
    n, p = args
    if p == 0:
        raise NE("p no puede ser 0")
    try:
        x = f.raiz_mod_p(n, p)
    except IncompatibleEquationError:
        raise NE(f"{n} no tiene raíz cuadrada módulo {p}")
    except ValueError as e:
        raise NE(str(e))
    return sorted({x, (-x) % abs(p)})

def h_ecCuadratica(args):
    """
    Espera 4 argumentos enteros (a,b,c,p), con p primo, y devuelve la lista ordenada de soluciones de
    ax^2 + bx + c = 0 (mod p): dos si son distintas y una si es una raíz doble.

    Excepciones: lanza NOP si el número de argumentos no es 4 y NE si la ecuación no tiene solución
    """
    if len(args) != 4:
        error_formato("ecCuadratica", "4 argumentos (a,b,c,p)", len(args), args)
    a, b, c, p = args
    if p == 0:
        raise NE("p no puede ser 0")
    try:
        x1, x2 = f.ecuacion_cuadratica(a, b, c, p)
    except IncompatibleEquationError as e:
        raise NE(str(e))
    except ValueError as e:
        raise NE(str(e))
    return sorted({x1, x2})

correspondencias = {             #utilizamos un diccionario para emparejar las funciones que se meten por argumentos y las funciones en el imatlab que lo ejecutan
    "primo": h_primo,
    "primos": h_primos,
    "factorizar": h_factorizar,
    "mcd": h_mcd,
    "coprimos": h_coprimos,
    "bezout": h_bezout,
    "pow": h_pow,
    "inv": h_inv,
    "euler": h_euler,
    "legendre": h_legendre,
    "resolverSistema": h_resolverSistema,
    "mcd_n": h_mcd_n,
    "bezout_n": h_bezout_n,
    "raiz": h_raiz,
    "ecCuadratica": h_ecCuadratica,
}

def hallar_resultado(solucion):
    """
    Solucion = (nombre_funcion, argumentos)
    - argumentos: lista/tupla de enteros, o (alist, blist, plist) para resolverSistema.
    Devuelve la función a ejecutar o lanza NOP/NE.
    """
    funcion, argumentos = solucion      #detecta lo que ha metido el usuario o el fichero por argumento y lo divide entre la función a hacer y lo necesario para ejecutarla (argumentos)
    funcion_asociada = correspondencias.get(funcion)    #busca la función asociada a la función definida previamente. Utiliza get para que no lance un KeyError
    if funcion_asociada is None:        # Si no se encuentra una función, lanzará el error NOP con un mensaje personalizado 
        raise NOP("función no reconocida")
    return funcion_asociada(argumentos)
        
def formatear_salida(funcion, resultado) -> str:
    """
    Convierte el resultado de una función de modular en el texto que imprime IMAT-LAB
    """
    if funcion in ("primo", "coprimos"):             # booleanos: Sí o No
        return "Sí" if resultado else "No"
    if funcion == "primos":                          # lista de primos separada por comas
        if not resultado:
            raise NE("no hay primos en el intervalo")
        return ", ".join(map(str, resultado))
    if funcion == "factorizar":
        if isinstance(resultado, int):               # n en {-1, 0, 1}
            return str(resultado)
        return ", ".join(f"{p}: {e}" for p, e in sorted(resultado.items()))   # factores en orden ascendente
    if funcion == "resolverSistema":
        r, m = resultado
        return f"{r} (mod {m})"
    if funcion in ("raiz", "ecCuadratica"):          # raíces en orden ascendente
        return ", ".join(map(str, resultado))
    return str(resultado)


def run_commands(fin:TextIO, fout:TextIO, detallado:bool=False):
    """ Recibe un manejador fin de un fichero de texto ya abierto para lectura y otro de un fichero de salida
    ya abierto para escritura y ejecuta línea por línea los comandos proporcionados por fin, escribiendo los resultados en fout.
    Si fin y fout no corresponden con la entrada y salida estándar, esta función ejecuta el modo de procesamiento
    por lotes de IMAT-LAB para la entrada fin, guardando el resultado en el fichero fout.

    Args:
        fin (TextIO): Fichero de entrada. Manejador de un fichero de texto ya abierto para lectura.
        fout (TextIO): Fichero de salida. Manejador de un fichero de texto ya abierto para escritura.
        detallado (bool): Si es True (modo interactivo), los errores se escriben con un mensaje
            explicativo ("NE: no existe inversa"); si es False (modo por lotes), solo el código
            "NE" o "NOP", como pide el enunciado.

    Returns: None

    Raises: None. Ningún comando puede detener la ejecución: cualquier error inesperado se
        escribe como NOP.

    Examples:
        run_commands(sys.stdin,sys.stdout) lanza el modo interactivo y ejecuta línea por línea los comandos que
            el usuario lanza desde la entrada estándar.
    """
    for i in fin:               #Itera linea a linea 
        linea = i.strip()       #Formatea para quitar espacios y saltos de línea 
        if linea == "":         #Una línea vacía termina la ejecución 
            break 
        try: 
            funcion, arg_str = detectar_funcion(linea)      #divide lo que ha metido el usuario o el fichero entre lo que es la función a ejecutar y los argumentos
            args = formatear_argumentos(funcion, arg_str)   #formatea los argumentos metidos para que se pueda utilizar en el modular 
            resultado = hallar_resultado((funcion, args))   #busca y ejecuta la función 
            salida = formatear_salida(funcion, resultado)
        except NE as e:
            salida = f"NE: {e}" if detallado else "NE"      #Errores por si no existe o no se puede ejecutar
        except NOP as e:
            salida = f"NOP: {e}" if detallado else "NOP"    #Errores de formato o de entrada no válida 
        except Exception as e:                              #Cualquier otro error no puede tumbar el programa 
            salida = f"NOP: error inesperado ({type(e).__name__}: {e})" if detallado else "NOP"
        fout.write(salida + "\n")


if __name__ == "__main__":
    args = sys.argv         # args[0] siempre es el nombre del script (imatlab.py)
    if len(args) == 1:      # sin argumentos: modo interactivo 
        print("IMAT-LAB · escribe un comando, por ejemplo pow(2,10,7). Línea vacía para salir.")
        while True:
            try:
                linea = input(">> ").strip()
            except (EOFError, KeyboardInterrupt):   #Ctrl+D o Ctrl+C también salen 
                print()
                break
            if not linea:                           #un Enter en blanco termina el modo interactivo 
                break
            run_commands(StringIO(linea + "\n"), sys.stdout, detallado=True)
    elif len(args) == 3:    # modo por lotes: python imatlab.py ENTRADA.txt SALIDA.txt 
        with open(args[1], "r", encoding="utf-8") as fin, \
             open(args[2], "w", encoding="utf-8") as fout:
            run_commands(fin, fout)
    else:
        print("Uso: python imatlab.py [ENTRADA.txt SALIDA.txt]", file=sys.stderr)
        sys.exit(2)
