import sqlite3

def get_connection():
    # Esto conecta a tu base de datos
    conn = sqlite3.connect('gym.db', check_same_thread=False)
    
    # Esto crea las tablas si no existen, para que no dé error
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Ejercicios (
            IdEjercicio INTEGER PRIMARY KEY AUTOINCREMENT, 
            Nombre TEXT UNIQUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Rutina_General (
            IdRutinaGen INTEGER PRIMARY KEY AUTOINCREMENT,
            DiaSemana TEXT,
            Bloque TEXT,
            IdEjercicio INTEGER,
            Repeticiones TEXT,
            Detalle TEXT,
            VideoUrl TEXT,
            TecnicaNota TEXT
        )
    """)
    conn.commit()
    return conn
