import sqlite3

def get_connection():
    # Conecta al archivo gym.db
    conn = sqlite3.connect('gym.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # ESTO CREA LAS TABLAS SI NO EXISTEN
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
    # Si tenés más tablas (como 'Socios' o 'Pagos'), agregalas acá abajo de la misma forma
    
    conn.commit()
    return conn
