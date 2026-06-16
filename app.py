import streamlit as st
from database.conexion import get_connection

st.title("Sistema Administrativo")
conn = get_connection()

try:
    # Probamos si la base de datos responde
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()
    st.write("Conexión exitosa. Tablas detectadas:", tablas)
except Exception as e:
    st.error(f"Error de base de datos: {e}")
