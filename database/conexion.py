import sqlite3
import os

def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'gym.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    
    # Crear tablas necesarias (si no existen)
    cursor.execute("CREATE TABLE IF NOT EXISTS Ejercicios (IdEjercicio INTEGER PRIMARY KEY AUTOINCREMENT, Nombre TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Planes (IdPlan INTEGER PRIMARY KEY AUTOINCREMENT, NombrePlan TEXT, Precio REAL, DuracionMeses INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Socios (IdSocio INTEGER PRIMARY KEY AUTOINCREMENT, Nombre TEXT, Apellido TEXT, DNI TEXT, Activo INTEGER, Saldo REAL, IdPlan INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Pagos (IdPago INTEGER PRIMARY KEY AUTOINCREMENT, IdSocio INTEGER, Monto REAL, MetodoPago TEXT, FechaPago TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Rutina_General (IdRutinaGen INTEGER PRIMARY KEY AUTOINCREMENT, DiaSemana TEXT, Bloque TEXT, IdEjercicio INTEGER, Repeticiones TEXT, Detalle TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Rutina_Excepcion (IdRutinaExc INTEGER PRIMARY KEY AUTOINCREMENT, IdSocio INTEGER, DiaSemana TEXT, Bloque TEXT, IdEjercicio INTEGER, Repeticiones TEXT, Detalle TEXT)")
    
    conn.commit()
    return conn
