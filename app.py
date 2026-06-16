import streamlit as st
import sqlite3
import os
from database.conexion import get_connection

# FUERZA LA CREACIÓN DE TABLAS SI NO EXISTEN
conn_temp = sqlite3.connect('gym.db')
cursor = conn_temp.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS Ejercicios (IdEjercicio INTEGER PRIMARY KEY AUTOINCREMENT, Nombre TEXT UNIQUE)")
cursor.execute("""CREATE TABLE IF NOT EXISTS Rutina_General (
        IdRutinaGen INTEGER PRIMARY KEY AUTOINCREMENT,
        DiaSemana TEXT,
        Bloque TEXT,
        IdEjercicio INTEGER,
        Repeticiones TEXT,
        Detalle TEXT,
        VideoUrl TEXT,
        TecnicaNota TEXT
    )""")
conn_temp.commit()
conn_temp.close()

st.title("Sistema Administrativo")
st.write("Tablas verificadas.")

st.divider()

# --- BOTÓN DE RESPALDO DE BASE DE DATOS ---
st.subheader("⚙️ Mantenimiento")

# Ruta de tu base de datos (gym.db está en la misma carpeta que este script)
db_path = 'gym.db'

if os.path.exists(db_path):
    with open(db_path, "rb") as file:
        st.download_button(
            label="💾 Descargar copia de seguridad (gym.db)",
            data=file,
            file_name="gym_backup.db",
            mime="application/x-sqlite3"
        )
else:
    st.error("No se encontró el archivo 'gym.db' para descargar.")
