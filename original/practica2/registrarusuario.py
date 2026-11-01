from rsa import *
import os
import sys  #importamos esta librería para terminar el programa si nos encontramos con algún error 

def nombre_valido(n): 
    """
    Recibe el nombre y valida si no se ha introducido un nombre vacío ya que es importante a la hora de crear los ficheros 
    Args: 
        n (str): El nombre del usuario
    """
    n = n.strip() 
    if not n: 
        print("Has introducido un nombre vacío")
        sys.exit(1)     #Si se ha introducido un nombre vacío, el programa terminará.
    return n 

if __name__ == "__main__": 
    
    nombre = nombre_valido(input("- Un nombre: "))      #El usuario introduce el nombre y lo validamos directamente.
    min_p = int(input("- El valor mínimo de cada primo usado para generar sus claves de RSA: "))    
    max_p = int(input("- El valor máximo de cada primo usado para generar sus claves de RSA: "))
    cifras_padding = int(input("- El número de cifras de padding para la comunicación con el usuario: "))
    while min_p >= max_p:   #Verificamos que el máximo sea mayor que el mínimo, si no lo es, le seguirá pidiendo al usuario que introduzca los números hasta que funcionen 
        print("Error:  el mínimo debería ser menor que el máximo")
        min_p = int(input("- El valor mínimo de cada primo usado para generar sus claves de RSA: "))
        max_p = int(input("- El valor máximo de cada primo usado para generar sus claves de RSA: "))
    
    n, e, d = generar_claves(min_p, max_p)  #El programa genera las claves RSA necesarias 
    
    carpeta = "Usuarios"    #Indicamos la carpeta donde guardaremos los ficheros 
    if not os.path.exists(carpeta): #Comprueba que no existe la carpeta Usuarios (donde guardaremos todos nuestros ficheros)
        os.makedirs(carpeta) #Creamos la carpeta "Usuarios".
    
    with open(f'{carpeta}/pub_{nombre}.txt', "w") as fichero:   #creamos un nuevo fichero en modo escritura dentro de la carpeta Usuarios 
        fichero.write(f'{n}')   #escribo las claves que acabo de generar en el fichero público 
        fichero.write(f'\n{e}')
        fichero.write(f'\n{cifras_padding}')

    with open(f'{carpeta}/priv_{nombre}.txt', "w") as fichero:  #creamos un nuevo fichero en modo escritura dentro de la carpeta Usuarios 
        fichero.write(f'{d}')   #escribo la clave privada en el fichero privado 