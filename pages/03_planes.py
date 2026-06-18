import streamlit as st
import pandas as pd
import requests
from database.conexion import get_connection

st.set_page_config(page_title="Gestión de Planes", layout="wide")
st.title("Configuración de Planes y Precios")

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
        cols = [c['name'].lower() for c in data['cols']] 
        clean_rows = []
        for row in rows:
            clean_row = [cell['value'] if isinstance(cell, dict) and 'value' in cell else cell for cell in row]
            clean_rows.append(clean_row)
        
        df = pd.DataFrame(clean_rows, columns=cols)
        # Convertimos explícitamente a número las columnas que corresponden
        for col in ['idplan', 'duracionmeses', 'precio']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error leyendo tabla: {e}")
        return pd.DataFrame()

# --- CARGA DE PLANES ---
df_planes = leer_tabla("SELECT IdPlan, NombrePlan, DuracionMeses, Precio FROM Planes")

# --- 1. FORMULARIO ---
with st.container(border=True):
    st.subheader("➕ Crear Nuevo Plan")
    col1, col2, col3 = st.columns(3)
    with col1: nombre_plan = st.text_input("Nombre del Plan")
    with col2: duracion_meses = st.number_input("Duración en Meses", min_value=1, value=1)
    with col3: precio_plan = st.number_input("Precio ($)", min_value=0.0, step=500.0)
        
    if st.button("Guardar Nuevo Plan"):
        if nombre_plan:
            ejecutar_query("INSERT INTO Planes (NombrePlan, DuracionMeses, Precio) VALUES (?, ?, ?)", 
                           [nombre_plan, int(duracion_meses), float(precio_plan)])
            st.rerun()
        else:
            st.error("El nombre no puede estar vacío.")

st.divider()

# --- 2. LISTADO Y EDICIÓN ---
st.subheader("📋 Planes Configurables")

if not df_planes.empty:
    df_mostrar = df_planes.copy()
    
    # Aplicamos formato de moneda para la vista limpia
    if 'precio' in df_mostrar.columns:
        df_mostrar['precio'] = df_mostrar['precio'].map('${:,.2f}'.format)
        
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

    st.subheader("✏️ Modificar o Eliminar Plan")
    
    # Todo en minúsculas para coincidir exactamente con el DataFrame
    opciones_planes = df_planes.apply(lambda row: f"{int(row['idplan'])} - {row['nombreplan']}", axis=1).tolist()
    plan_seleccionado = st.selectbox("Seleccionar:", opciones_planes)
    
    id_plan_sel = int(plan_seleccionado.split(" - ")[0])
    datos_plan = df_planes[df_planes['idplan'] == id_plan_sel].iloc[0]
    
    col_edit, col_del = st.columns(2)
    with col_edit:
        st.write("⚙️ **Editar Valores**")
        nuevo_nombre = st.text_input("Nombre", value=str(datos_plan['nombreplan']))
        nueva_duracion = st.number_input("Meses", value=int(datos_plan['duracionmeses']))
        nuevo_precio = st.number_input("Precio ($)", value=float(datos_plan['precio']))
        
        if st.button("Actualizar Plan"):
            ejecutar_query("UPDATE Planes SET NombrePlan=?, DuracionMeses=?, Precio=? WHERE IdPlan=?",
                           [nuevo_nombre, int(nueva_duracion), float(nuevo_precio), id_plan_sel])
            st.rerun()
            
    with col_del:
        if st.button("🗑️ Eliminar este plan", type="primary"):
            ejecutar_query("DELETE FROM Planes WHERE IdPlan=?", [id_plan_sel])
            st.rerun()
else:
    st.info("No hay planes cargados.")
