import streamlit as st
from database.conexion import get_connection

st.title("Sistema Administrativo")
conn = get_connection() # Esto crea las tablas si faltan

st.write("¡El sistema está conectado y listo!")
st.write("👈 Usá el menú de la izquierda.")
