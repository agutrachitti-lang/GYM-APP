import streamlit as st
import pandas as pd
import requests
from database.conexion import get_connection

st.set_page_config(page_title="Gestión de Planes", layout="wide")
st.title("Configuración de Planes y Precios")

url, token = get_connection()

def ejecutar_query(query, params=()):
    # Traductor estricto para que Turso no rechace los números
    formatted_params = []
    for p in params:
        if p is None:
            formatted_params.append({"type": "null"})
        elif isinstance(p, int):
            formatted_params.append({"type": "integer", "value": str(p)})
        elif isinstance(p, float):
            formatted_params.append({"type": "float", "value": float(p)})
        else:
            formatted_params.append({"type": "text", "value": str(p)})

    payload = {
        "requests": [{"type": "execute", "stmt": {"sql": query, "args": formatted_params}}]
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{url}/v2/pipeline", json=payload, headers=headers)
    
    res_json = response.json()
    
    # Escudo antiaéreo para ver errores
    try:
        for res in res_json.get("results", []):
            if res.get("type") == "error":
                st.error(f"⚠️ Error de base de datos: {res.get('error', {}).get('message')}")
    except:
        pass
        
    return res_json

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
            # BALA DE PLATA: Asignamos el ID manualmente por si Turso falla
            nuevo_id = 1
            if not df_planes.empty and pd.notna(df_planes['idplan'].max()):
                nuevo_id = int(df_planes['idplan'].max()) + 1
                
            res = ejecutar_query(
                "INSERT INTO Planes (IdPlan, NombrePlan, DuracionMeses, Precio) VALUES (?, ?, ?, ?)", 
                [nuevo_id, nombre_plan.strip(), int(duracion_meses), float(precio_plan)]
            )
            
            hay_error = any(r.get("type") == "error" for r in res.get("results", []))
            if not hay_error:
                st.success("¡Plan creado!")
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
    
    # Escudo Anti-None por si quedó algún plan viejo sin ID
    opciones_planes = df_planes.apply(
        lambda row: f"{int(row['idplan']) if pd.notna(row['idplan']) else 0} - {row['nombreplan']}", axis=1
    ).tolist()
    
    plan_seleccionado = st.selectbox("Seleccionar:", opciones_planes)
    id_plan_sel = int(plan_seleccionado.split(" - ")[0])
    
    if id_plan_sel == 0:
        datos_plan = df_planes[df_planes['idplan'].isna()].iloc[0]
    else:
        datos_plan = df_planes[df_planes['idplan'] == id_plan_sel].iloc[0]
    
    col_edit, col_del = st.columns(2)
    with col_edit:
        st.write("⚙️ **Editar Valores**")
        nuevo_nombre = st.text_input("Nombre", value=str(datos_plan['nombreplan']))
        nueva_duracion = st.number_input("Meses", value=int(datos_plan['duracionmeses']) if pd.notna(datos_plan['duracionmeses']) else 1)
        nuevo_precio = st.number_input("Precio ($)", value=float(datos_plan['precio']) if pd.notna(datos_plan['precio']) else 0.0)
        
        if st.button("Actualizar Plan"):
            if id_plan_sel == 0:
                res = ejecutar_query(
                    "UPDATE Planes SET NombrePlan=?, DuracionMeses=?, Precio=? WHERE NombrePlan=?",
                    [nuevo_nombre.strip(), int(nueva_duracion), float(nuevo_precio), str(datos_plan['nombreplan'])]
                )
            else:
                res = ejecutar_query(
                    "UPDATE Planes SET NombrePlan=?, DuracionMeses=?, Precio=? WHERE IdPlan=?",
                    [nuevo_nombre.strip(), int(nueva_duracion), float(nuevo_precio), id_plan_sel]
                )
            
            hay_error = any(r.get("type") == "error" for r in res.get("results", []))
            if not hay_error:
                st.rerun()
            
    with col_del:
        st.write("🗑️ **Eliminar Plan**")
        with st.popover("🗑️ Eliminar"):
            st.warning(f"¿Seguro que querés borrar {datos_plan['nombreplan']}?")
            if st.button("Sí, borrar plan", type="primary"):
                if id_plan_sel == 0:
                    ejecutar_query("DELETE FROM Planes WHERE NombrePlan=?", [str(datos_plan['nombreplan'])])
                else:
                    ejecutar_query("DELETE FROM Planes WHERE IdPlan=?", [id_plan_sel])
                st.rerun()
else:
    st.info("No hay planes cargados.")
