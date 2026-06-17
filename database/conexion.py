import streamlit as st

import sqlite3

import requests



# Esta función conecta a Turso usando su API HTTP (más estable)

def get_connection():

    # URL de Turso (usando la API en lugar de libsql://)

    url = st.secrets["TURSO_DATABASE_URL"].replace("libsql://", "https://")

    token = st.secrets["TURSO_AUTH_TOKEN"]

    

    # Turso vía HTTP no es una "conexión" tradicional, 

    # pero podemos emular la estructura que pide Pandas con un objeto simple.

    # Como queremos que pd.read_sql funcione, lo más limpio es usar 

    # el driver estándar de sqlite3 y conectarlo a un archivo temporal local

    # que se sincroniza, O simplificar el acceso a los datos:

    

    return url, token

