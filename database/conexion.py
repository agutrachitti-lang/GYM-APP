import sqlite3
import os

def get_connection():
    # Buscamos el archivo en la raíz del proyecto (donde lo subiste a GitHub)
    db_path = os.path.join(os.getcwd(), 'gym.db')
    
    # Abrimos la conexión. Si el archivo existe (como en GitHub), lo usa.
    # NO ejecutamos CREATE TABLE ni nada más aquí para no alterar el archivo.
    conn = sqlite3.connect(db_path, check_same_thread=False)
    return conn
