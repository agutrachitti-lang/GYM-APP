import streamlit as st
import pandas as pd
import requests
from database.conexion import get_connection

st.set_page_config(page_title="Gestión de Socios", layout="wide")
st.title("Socios del Gimnasio")

# --- ADAPTACIÓN PARA TU CONEXIÓN ---
url, token = get_connection()

def ejecutar_query(query, params=()):
    payload = {
        "requests": [{"type": "execute", "stmt": {"sql": query, "args": params}}]
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{url}/v2/pipeline", json=payload, headers=headers)
    return response.json()

def leer_tabla(query):
    res = ejecutar_query(query)
    try:
        data = res['results'][0]['response']['result']
        rows = data['rows']
        cols = [c['name'].lower() for c in data['cols']] # Forzamos minúsculas
        clean_rows = []
        for row in rows:
            clean_row = [cell['value'] if isinstance(cell, dict) and 'value' in cell else cell for cell in row]
            clean_rows.append(clean_row)
            
        df = pd.DataFrame(clean_rows, columns=cols)
        # Convertimos explícitamente a número las columnas que corresponden
        for col in ['idsocio', 'dni', 'idplan', 'saldo', 'activo']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e:
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
        # Usamos minúsculas: 'nombreplan'
        lista_planes = df_planes['nombreplan'].tolist() if not df_planes.empty else ["Sin planes"]
        plan_elegido = st.selectbox("Seleccionar Plan", lista_planes)

    if st.button("Guardar Socio"):
        if nombre and apellido and dni:
            id_plan = None
            if not df_planes.empty and plan_elegido != "Sin planes":
                # Buscamos usando minúsculas
                id_plan = int(df_planes[df_planes['nombreplan'] == plan_elegido]['idplan'].iloc[0])
            
            ejecutar_query(
                "INSERT INTO Socios (Nombre, Apellido, DNI, IdPlan, Activo) VALUES (?,?,?,?,1)", 
                [nombre, apellido, dni, id_plan]
            )
            st.success("Socio guardado exitosamente.")
            st.rerun()
        else:
            st.error("Por favor completa los campos obligatorios.")

st.divider()

# --- LISTADO Y GESTIÓN ---
st.subheader("Listado Actual")
if not df_socios.empty:
    st.dataframe(df_socios, use_container_width=True, hide_index=True)
    
    # Formateamos el selector usando las variables en minúscula y forzando idsocio a entero
    opciones_socios = df_socios.apply(lambda r: f"{int(r['idsocio'])} - {r['nombre']} {r['apellido']}", axis=1).tolist()
    socio_sel = st.selectbox("Seleccionar para gestionar:", opciones_socios)
    
    if st.button("Eliminar seleccionado", type="primary"):
        id_a_borrar = int(socio_sel.split(" - ")[0])
        ejecutar_query("DELETE FROM Socios WHERE IdSocio = ?", [id_a_borrar])
        st.rerun()
else:
    st.info("No hay socios registrados.")
