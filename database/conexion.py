import streamlit as st
from sqlalchemy import create_engine

def get_connection():
    # Convertimos la URL de libsql a formato compatible para SQLAlchemy
    # Turso funciona con el driver 'sqlite' si le pasamos la URL correctamente
    db_url = st.secrets["TURSO_DATABASE_URL"]
    
    # SQLAlchemy requiere un formato específico para sqlite
    # Como Turso es remoto, usamos un motor que apunte a la nube
    engine = create_engine(f"sqlite:///:memory:") # Esto es para operar en memoria
    
    # NOTA: Para que pd.read_sql lea de Turso, lo más estable es:
    return db_url, st.secrets["TURSO_AUTH_TOKEN"]
