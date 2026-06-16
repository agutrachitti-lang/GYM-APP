import sqlite3
import os

def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'gym.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    
    # Crear la estructura exacta que tu código espera
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Planes (
            IdPlan INTEGER PRIMARY KEY AUTOINCREMENT, 
            NombrePlan TEXT, 
            Precio REAL, 
            DuracionMeses INTEGER
        )
    """)
    conn.commit()
    return conn
