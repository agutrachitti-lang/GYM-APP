import streamlit as st
import libsql_experimental as sqlite3

def get_connection():
    db_url = st.secrets["libsql://gymdb-agutrachitti-lang.aws-us-east-1.turso.io"]
    auth_token = st.secrets["eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODE3MTkyNDEsImlkIjoiMDE5ZWQ2YmMtNzAwMS03MzEzLTllOGYtNzcyMjE2NTU3ZmU0IiwicmlkIjoiMTVlNjFkYzUtMGQzYS00ODc1LTg3OWQtMTA0OTMyOTU0ZGZkIn0.Q-6OhbsrqfuHz4ROTrpNVZXNTfCKQM1Jl9FykIsVSVsb2LVyoTY23n6zsoA95GhSS0HAEPkeMZJAdfcMg3deDw"]
    
    conn = sqlite3.connect(database=db_url, auth_token=auth_token)
    conn.check_same_thread = False
    
    # FORZAR CREACIÓN DE TABLAS SI NO EXISTEN
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Planes (
        IdPlan INTEGER PRIMARY KEY AUTOINCREMENT, 
        NombrePlan TEXT, DuracionMeses INTEGER, Precio REAL
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Socios (
        IdSocio INTEGER PRIMARY KEY AUTOINCREMENT, 
        Nombre TEXT, Apellido TEXT, DNI TEXT UNIQUE, IdPlan INTEGER, 
        FechaAlta TEXT, FechaVencimiento TEXT, Saldo REAL, Activo INTEGER DEFAULT 1
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pagos (
        IdPago INTEGER PRIMARY KEY AUTOINCREMENT, 
        IdSocio INTEGER, Monto REAL, MetodoPago TEXT, FechaPago TEXT
    )""")
    conn.commit()
    
    return conn
