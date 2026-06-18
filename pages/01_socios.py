import streamlit as st
import pandas as pd
import requests
from database.conexion import get_connection

# --- ADAPTACIÓN PARA QUE FUNCIONE CON TU CONEXIÓN ---
url, token = get_connection()

def ejecutar_query(query, params=()):
    # Esta función reemplaza a los 'conn.execute'
    payload = {"statements": [{"q": query, "params": params}]}
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{url}/v2/pipeline", json=payload, headers=headers)
    return response.json()

def leer_tabla(query):
    # Esta función reemplaza a los 'pd.read_sql'
    res = ejecutar_query(query)
    try:
        data = res['results'][0]['response']['result']
        # Convertimos las filas de Turso a DataFrame
        return pd.DataFrame(data['rows'], columns=[c['name'] for c in data['cols']])
    except:
        return pd.DataFrame()

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
