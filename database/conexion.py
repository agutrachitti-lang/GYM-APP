import sqlite3

def get_connection():
    # Esto crea el archivo 'gym.db' automáticamente si no existe
    conn = sqlite3.connect('gym.db', check_same_thread=False)
    return conn