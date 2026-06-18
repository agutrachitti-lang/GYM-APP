import streamlit as st
import pandas as pd
import requests
from database.conexion import get_connection

st.set_page_config(page_title="Gestión de Socios", layout="wide")
st.title("Socios del Gimnasio")

# --- ADAPTACIÓN PARA TU CONEXIÓN ---
url, token = get_connection()

def ejecutar_query(query, params=()):
    payload = {"statements": [{"q": query, "params": params}]}
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{url}/v2/pipeline", json=payload, headers=headers)
    return response.json()

def leer_tabla(query):
    res = ejecutar_query(query)
    try:
        data = res['results'][0]['response']['result']
        return pd.DataFrame(data['rows'], columns=[c['name'] for c in data['cols']])
    except:
        return pd.DataFrame()

# --- CARGAR DATOS ---
df_socios = leer_tabla("SELECT S.*, P.NombrePlan FROM Socios S LEFT JOIN Planes P ON S.IdPlan = P.IdPlan")
df_planes = leer_tabla("SELECT * FROM Planes")

# --- PANEL DE ALTA ---
with st.container(border=True):
    st.subheader("Agregar Nuevo Socio")
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
    with col2:
        dni = st.text_input("DNI")
        # Cargamos los planes dinámicamente desde la BD
        lista_planes = df_planes['NombrePlan'].tolist() if not df_planes.empty else ["Sin planes"]
        plan_elegido = st.selectbox("Seleccionar Plan", lista_planes)

    if st.button("Guardar Socio"):
        if nombre and apellido and dni:
            # Buscamos el ID del plan seleccionado
            id_plan = df_planes[df_planes['NombrePlan'] == plan_elegido]['IdPlan'].iloc[0] if not df_planes.empty else None
            
            ejecutar_query(
                "INSERT INTO Socios (Nombre, Apellido, DNI, IdPlan, Activo) VALUES (?,?,?,?,1)", 
                [nombre, apellido, dni, id_plan]
            )
            st.success("Socio guardado")
            st.rerun()
        else:
            st.error("Por favor completa los campos obligatorios.")

st.divider()

# --- LISTADO Y GESTIÓN ---
st.subheader("Listado Actual")
if not df_socios.empty:
    st.dataframe(df_socios, use_container_width=True)
    
    socio_sel = st.selectbox("Seleccionar para gestionar:", df_socios.apply(lambda r: f"{r['IdSocio']} - {r['Nombre']} {r['Apellido']}", axis=1))
    
    if st.button("Eliminar seleccionado"):
        id_a_borrar = socio_sel.split(" - ")[0]
        ejecutar_query("DELETE FROM Socios WHERE IdSocio = ?", [id_a_borrar])
        st.rerun()
else:
    st.info("No hay socios registrados.")
