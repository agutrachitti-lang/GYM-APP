import streamlit as st
import sqlite3
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
