import sqlite3

def get_connection():
    try:
        conn = sqlite3.connect('gym.db', check_same_thread=False)
        # Esto crea las tablas si no existen
        cursor = conn.cursor()
        tablas = [
            "CREATE TABLE IF NOT EXISTS Ejercicios (IdEjercicio INTEGER PRIMARY KEY AUTOINCREMENT, Nombre TEXT UNIQUE)",
            "CREATE TABLE IF NOT EXISTS Rutina_General (IdRutinaGen INTEGER PRIMARY KEY AUTOINCREMENT, DiaSemana TEXT, Bloque TEXT, IdEjercicio INTEGER, Repeticiones TEXT, Detalle TEXT, VideoUrl TEXT, TecnicaNota TEXT)",
            "CREATE TABLE IF NOT EXISTS Socios (IdSocio INTEGER PRIMARY KEY AUTOINCREMENT, Nombre TEXT, DNI TEXT, FechaVencimiento TEXT)",
            "CREATE TABLE IF NOT EXISTS Planes (IdPlan INTEGER PRIMARY KEY AUTOINCREMENT, NombrePlan TEXT, Precio REAL)",
            "CREATE TABLE IF NOT EXISTS Pagos (IdPago INTEGER PRIMARY KEY AUTOINCREMENT, IdSocio INTEGER, FechaPago TEXT, Monto REAL)"
        ]
        for t in tablas:
            cursor.execute(t)
        conn.commit()
        return conn
    except Exception as e:
        print(f"Error en la base de datos: {e}")
        return None
