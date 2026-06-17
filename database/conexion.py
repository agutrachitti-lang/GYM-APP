import streamlit as st
import libsql_experimental as sqlite3

def get_connection():
    # Estas variables deben estar en Secrets de Streamlit Cloud
    db_url = st.secrets["TURSO_DATABASE_URL"]
    auth_token = st.secrets["TURSO_AUTH_TOKEN"]
    
    # Conectamos
    conn = sqlite3.connect(database=db_url, auth_token=auth_token)
    
    # IMPORTANTE: Desactivamos el modo de bloqueo de hilos de sqlite3 
    # para que Streamlit pueda usar la conexión sin errores.
    conn.check_same_thread = False
    
    return conn
