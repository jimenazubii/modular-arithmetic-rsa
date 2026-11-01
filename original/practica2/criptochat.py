import sys
from rsa import *    # Importamos todas las funciones necesarias del módulo rsa
import os

def cargar_clave_publica(usuario:str): 
    """
    Carga la clave pública de un usuario desde la carpeta 'Usuarios'.
    Si el archivo existe, devuelve una tupla (n, e, padding), si no, devuelve None.
    """
    carpeta = "Usuarios"
    clave_pub = None 

    # Buscamos el fichero de clave pública del usuario
    if os.path.exists(f'{carpeta}/pub_{usuario}.txt'):
        with open(f"{carpeta}/pub_{usuario}.txt", "r") as f:
            lineas = f.read().split("\n")   # Separamos líneas directamente
            n = int(lineas[0])
            e = int(lineas[1])
            n_padding = int(lineas[2])
            clave_pub = (n, e, n_padding)
    return clave_pub

def cargar_clave_privada(usuario:str): 
    """
    Carga la clave privada de un usuario desde la carpeta 'Usuarios'.
    Si el archivo existe, devuelve d (int), si no, devuelve None.
    """
    carpeta = "Usuarios"
    clave_priv = None 

    # Buscamos el fichero de clave privada del usuario
    if os.path.exists(f"{carpeta}/priv_{usuario}.txt"): 
        with open(f"{carpeta}/priv_{usuario}.txt", "r") as f: 
            clave_priv = int(f.read().strip())
    return clave_priv 

if __name__ == "__main__": 
    # Comprobamos que se han pasado los 2 usuarios como argumentos
    args = sys.argv 
    if len(args) != 3: 
        print("Uso correcto: python criptochat.py <usuario1> <usuario2>")    
    else:
        usuario1 = args[1]
        usuario2 = args[2]

        # Cargamos claves de los usuarios
        clave_pub_u1 = cargar_clave_publica(usuario1)
        clave_priv_u1 = cargar_clave_privada(usuario1)
        clave_pub_u2 = cargar_clave_publica(usuario2)
    
        # Comprobamos que existan las claves necesarias
        if not clave_pub_u1:
            print("La clave pública del usuario 1 no existe.")
        elif not clave_pub_u2: 
            print("La clave pública del usuario 2 no existe.")
        elif not clave_priv_u1: 
            print("La clave privada del usuario 1 no existe.")
        else: 
            opcion = ""
            while opcion != "S": 
                opcion = input("¿Qué quieres hacer: cifrar (C), descifrar (D) o salir (S)? ").upper()
                
                if opcion == "C": 
                    # Cifrado: usuario1 envía un mensaje cifrado con la clave pública de usuario2
                    mensaje_a_cifrar = input("Introduce el texto que deseas cifrar: ")
                    mensaje_cifrado = cifrar_cadena_rsa(mensaje_a_cifrar, clave_pub_u2[0], clave_pub_u2[1], clave_pub_u2[2])

                    #convertimos la lista a un texto limpio para poder presentarlo por pantalla 
                    # Recorremos la lista y usamos " ".join para convertirla en un string, separando cada número con un espacio
                    mensaje_str = " ".join(str(i) for i in mensaje_cifrado) 

                    print("Mensaje cifrado: ", mensaje_str)

                elif opcion == 'D': 
                    # Descifrado: usuario1 descifra con su clave privada
                    mensaje_cifrado_str = input("Introduce el mensaje cifrado que deseas descifrar: ")
                    mensaje_cifrado = [int(i) for i in mensaje_cifrado_str.split(" ")]  #convertimos el menaje cifrado a ints para que se pueda utilizar en la función 
                    mensaje_descifrado = descifrar_cadena_rsa(mensaje_cifrado, clave_pub_u1[0], clave_priv_u1, clave_pub_u1[2])
                    print("Mensaje descifrado:", mensaje_descifrado)

                elif opcion != "S": #salir del programa
                    print("Opción no válida. Por favor, selecciona C, D o S.")



