import sqlite3
import os

def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'gym.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    
    # Creamos las tablas con TODAS las columnas que usas en tus INSERT
    cursor.execute("""CREATE TABLE IF NOT EXISTS Socios (
        IdSocio INTEGER PRIMARY KEY AUTOINCREMENT, 
        Nombre TEXT, 
        Apellido TEXT, 
        DNI TEXT, 
        FechaAlta TEXT, 
        FechaVencimiento TEXT, 
        Saldo REAL, 
        Activo INTEGER, 
        IdPlan INTEGER
    )""")
    
    # Aseguramos que existan las otras tablas
    cursor.execute("CREATE TABLE IF NOT EXISTS Planes (IdPlan INTEGER PRIMARY KEY AUTOINCREMENT, NombrePlan TEXT, Precio REAL, DuracionMeses INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Ejercicios (IdEjercicio INTEGER PRIMARY KEY AUTOINCREMENT, Nombre TEXT UNIQUE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Pagos (IdPago INTEGER PRIMARY KEY AUTOINCREMENT, IdSocio INTEGER, Monto REAL, MetodoPago TEXT, FechaPago TEXT)")
    
    conn.commit()
    return conn
