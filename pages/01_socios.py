import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from database.conexion import get_connection

st.set_page_config(page_title="Gestión de Socios", layout="wide")
st.title("Socios del Gimnasio")

# --- CONEXIÓN ---
url, token = get_connection()

# --- FUNCIÓN DE LECTURA (API DE TURSO) ---
def ejecutar_query(query, params=None):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"statements": [{"q": query, "params": params or []}]}
    response = requests.post(f"{url}/v2/pipeline", json=payload, headers=headers)
    return response.json()

# --- CARGAR DATOS ---
def obtener_df():
    res = ejecutar_query("SELECT S.*, P.NombrePlan FROM Socios S LEFT JOIN Planes P ON S.IdPlan = P.IdPlan")
    try:
        data = res['results'][0]['response']['result']
        return pd.DataFrame(data['rows'], columns=[c['name'] for c in data['cols']])
    except:
        return pd.DataFrame()

df_socios = obtener_df()

# --- PANEL DE ALTA ---
with st.container(border=True):
    st.subheader("Agregar Nuevo Socio")
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
    with col2:
        dni = st.text_input("DNI")
        plan_elegido = st.selectbox("Plan", ["Plan A", "Plan B"]) # Ajusta según tu tabla Planes

    if st.button("Guardar Socio"):
        ejecutar_query("INSERT INTO Socios (Nombre, Apellido, DNI, Activo) VALUES (?,?,?,1)", [nombre, apellido, dni])
        st.success("Socio guardado")
        st.rerun()

st.divider()

# --- LISTADO Y GESTIÓN ---
st.subheader("Listado Actual")
if not df_socios.empty:
    st.dataframe(df_socios, use_container_width=True)
    
    socio_sel = st.selectbox("Seleccionar para gestionar:", df_socios.apply(lambda r: f"{r['IdSocio']} - {r['Nombre']}", axis=1))
    
    if st.button("Eliminar seleccionado"):
        id_a_borrar = socio_sel.split(" - ")[0]
        ejecutar_query("DELETE FROM Socios WHERE IdSocio = ?", [id_a_borrar])
        st.rerun()
else:
    st.info("No hay socios.")
