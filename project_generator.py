import sys
from horrocrux.models.generador import GeneradorProyecto
from horrocrux.models.menu import ejecutar_menu

if __name__ == "__main__":

    try:
        nombre = str(sys.argv[1])
        # nombre = "prueba"
    except Exception as _:
        nombre=""

    try:
        # carpeta = "prueba"
        carpeta = str(sys.argv[2])
    except Exception as _:
        carpeta=""

    generador = GeneradorProyecto(nombre,carpeta)

    ejecutar_menu(generador)


