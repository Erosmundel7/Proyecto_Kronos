''' ESTE MODULO ES PARA LA CONEXION A LA BASE DE DATOS '''

import sqlite3
import os 

def conectar_db():

    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_db = os.path.join(directorio_actual,"ProyectoKronos.db" )

    # se crea la conexion con la base de datos
    conex = sqlite3.connect(ruta_db)

    # Activo las FK
    conex.execute("PRAGMA foreign_keys = ON")

    # Retorno el objeto para que devuelva la conexion
    return conex


