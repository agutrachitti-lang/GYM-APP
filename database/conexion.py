import sqlite3

def get_connection():
    conn = sqlite3.connect('gym.db', check_same_thread=False)
    # Creamos las tablas si no existen para evitar el error de "no encuentra la tabla"
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
            TecnicaNota TEXT,
            FOREIGN KEY(IdEjercicio) REFERENCES Ejercicios(IdEjercicio)
        )
    """)
    conn.commit()
    return conn
