import sqlite3

def crear_todo():
    conn = sqlite3.connect('gym.db')
    cursor = conn.cursor()
    
    # Crear tablas
    cursor.execute("CREATE TABLE IF NOT EXISTS Ejercicios (IdEjercicio INTEGER PRIMARY KEY AUTOINCREMENT, Nombre TEXT UNIQUE)")
    cursor.execute("""CREATE TABLE IF NOT EXISTS Rutina_General (
            IdRutinaGen INTEGER PRIMARY KEY AUTOINCREMENT,
            DiaSemana TEXT,
            Bloque TEXT,
            IdEjercicio INTEGER,
            Repeticiones TEXT,
            Detalle TEXT,
            VideoUrl TEXT,
            TecnicaNota TEXT
        )""")
    
    conn.commit()
    conn.close()
    print("Tablas creadas exitosamente.")

if __name__ == "__main__":
    crear_todo()
