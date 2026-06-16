import sqlite3
import os

def get_connection():
    # Esta ruta asegura que siempre busque el archivo gym.db en la misma carpeta que el código
    db_path = os.path.join(os.path.dirname(__file__), 'gym.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    
    # Crear las tablas idénticas a tu SQL Server
    queries = [
        "CREATE TABLE IF NOT EXISTS Ejercicios (IdEjercicio INTEGER PRIMARY KEY AUTOINCREMENT, Nombre TEXT)",
        "CREATE TABLE IF NOT EXISTS Pagos (IdPago INTEGER PRIMARY KEY AUTOINCREMENT, IdSocio INTEGER, FechaPago TEXT, Monto REAL)",
        "CREATE TABLE IF NOT EXISTS Planes (IdPlan INTEGER PRIMARY KEY AUTOINCREMENT, NombrePlan TEXT, Precio REAL, DuracionMeses INTEGER)",
        "CREATE TABLE IF NOT EXISTS Registro_Alumno (IdRegistro INTEGER PRIMARY KEY AUTOINCREMENT, IdRutina INTEGER, Repeticiones INTEGER, KG REAL)",
        "CREATE TABLE IF NOT EXISTS Rutina_Excepcion (IdExcepcion INTEGER PRIMARY KEY AUTOINCREMENT, IdRutina INTEGER, Fecha TEXT)",
        "CREATE TABLE IF NOT EXISTS Rutina_General (IdRutinaGen INTEGER PRIMARY KEY AUTOINCREMENT, DiaSemana TEXT, Bloque TEXT, IdEjercicio INTEGER, Repeticiones TEXT, Detalle TEXT, VideoUrl TEXT, TecnicaNota TEXT)",
        "CREATE TABLE IF NOT EXISTS Rutinas (IdRutina INTEGER PRIMARY KEY AUTOINCREMENT, NombreRutina TEXT)",
        "CREATE TABLE IF NOT EXISTS Socios (IdSocio INTEGER PRIMARY KEY AUTOINCREMENT, Nombre TEXT, Apellido TEXT, DNI TEXT, FechaVencimiento TEXT, IdPlan INTEGER)"
    ]
    
    cursor = conn.cursor()
    for q in queries:
        cursor.execute(q)
    conn.commit()
    return conn
