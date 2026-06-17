import streamlit as st
import libsql_experimental as sqlite3

def get_connection():
    try:
        # Intentamos obtener los secretos
        db_url = st.secrets["TURSO_DATABASE_URL"]
        auth_token = st.secrets["TURSO_AUTH_TOKEN"]
        
        conn = sqlite3.connect(database=db_url, auth_token=auth_token)
        conn.check_same_thread = False
        
        # Probamos una consulta simple para ver si la tabla existe
        conn.execute("SELECT 1 FROM Socios LIMIT 1")
        return conn
        
    except Exception as e:
        # Si falla, mostramos el error real en pantalla
        st.error(f"¡Error de conexión! Revisa los Secrets en Streamlit Cloud. Detalle: {e}")
        st.stop()
