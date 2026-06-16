import sqlite3

def get_connection():
    return sqlite3.connect('gym.db', check_same_thread=False)

def controlar_vencimientos_automaticos():
    # Aquí iría el código que antes tenías para controlar vencimientos
    # Si no tenés el código a mano, dejala vacía para que no tire error:
    pass
