import streamlit as st
import libsql_experimental as sqlite3

def get_connection():
    # 1. Traemos las credenciales desde los secretos de Streamlit
    db_url = st.secrets["TURSO_DATABASE_URL"]
    auth_token = st.secrets["TURSO_AUTH_TOKEN"]
    
    # 2. Conectamos a Turso
    conn = sqlite3.connect(database=db_url, auth_token=auth_token)
    
    # 3. Creamos las tablas si es la primera vez que arranca (la BD está en blanco)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Planes (
        IdPlan INTEGER PRIMARY KEY AUTOINCREMENT,
        NombrePlan TEXT NOT NULL,
        DuracionMeses INTEGER NOT NULL,
        Precio REAL NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Socios (
        IdSocio INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre TEXT NOT NULL,
        Apellido TEXT NOT NULL,
        DNI TEXT NOT NULL UNIQUE,
        IdPlan INTEGER,
        FechaAlta TEXT,
        FechaVencimiento TEXT,
        Saldo REAL DEFAULT 0,
        Activo INTEGER DEFAULT 1,
        FOREIGN KEY(IdPlan) REFERENCES Planes(IdPlan)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pagos (
        IdPago INTEGER PRIMARY KEY AUTOINCREMENT,
        IdSocio INTEGER,
        Monto REAL,
        MetodoPago TEXT,
        FechaPago TEXT,
        FOREIGN KEY(IdSocio) REFERENCES Socios(IdSocio)
    )
    """)
    conn.commit()
    
    return conn
