import sqlite3

def get_connection():
    # Nos conectamos
    conn = sqlite3.connect('gym.db', check_same_thread=False)
    
    # Lista de todas las tablas que tu sistema necesita
    tablas = [
        "CREATE TABLE IF NOT EXISTS Ejercicios (IdEjercicio INTEGER PRIMARY KEY AUTOINCREMENT, Nombre TEXT UNIQUE)",
        "CREATE TABLE IF NOT EXISTS Rutina_General (IdRutinaGen INTEGER PRIMARY KEY AUTOINCREMENT, DiaSemana TEXT, Bloque TEXT, IdEjercicio INTEGER, Repeticiones TEXT, Detalle TEXT, VideoUrl TEXT, TecnicaNota TEXT)",
        "CREATE TABLE IF NOT EXISTS Socios (IdSocio INTEGER PRIMARY KEY AUTOINCREMENT, Nombre TEXT, DNI TEXT, FechaVencimiento TEXT)",
        "CREATE TABLE IF NOT EXISTS Planes (IdPlan INTEGER PRIMARY KEY AUTOINCREMENT, NombrePlan TEXT, Precio REAL)",
        "CREATE TABLE IF NOT EXISTS Pagos (IdPago INTEGER PRIMARY KEY AUTOINCREMENT, IdSocio INTEGER, FechaPago TEXT, Monto REAL)"
    ]
    
    cursor = conn.cursor()
    for t in tablas:
        cursor.execute(t)
    conn.commit()
    return conn
