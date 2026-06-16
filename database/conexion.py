import sqlite3

def get_connection():
    # Se conecta al archivo gym.db en la nube
    conn = sqlite3.connect('gym.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Lista de tablas necesarias para que no te dé error
    tablas = [
        """CREATE TABLE IF NOT EXISTS Ejercicios (
            IdEjercicio INTEGER PRIMARY KEY AUTOINCREMENT, 
            Nombre TEXT UNIQUE
        )""",
        """CREATE TABLE IF NOT EXISTS Rutina_General (
            IdRutinaGen INTEGER PRIMARY KEY AUTOINCREMENT,
            DiaSemana TEXT,
            Bloque TEXT,
            IdEjercicio INTEGER,
            Repeticiones TEXT,
            Detalle TEXT,
            VideoUrl TEXT,
            TecnicaNota TEXT
        )"""
    ]
    
    for tabla in tablas:
        cursor.execute(tabla)
        
    conn.commit()
    return conn
