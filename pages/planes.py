import streamlit as st
import pandas as pd
from database.conexion import get_connection

st.set_page_config(page_title="Gestión de Planes", layout="wide")
st.title("Configuración de Planes y Precios")

conn = get_connection()

# --- CARGA SEGURA DE PLANES ---
try:
    df_planes = pd.read_sql("SELECT IdPlan, NombrePlan, DuracionMeses, Precio FROM Planes", conn)
except:
    df_planes = pd.DataFrame(columns=['IdPlan', 'NombrePlan', 'DuracionMeses', 'Precio'])

# --- 1. FORMULARIO PARA CREAR UN PLAN NUEVO ---
with st.form("form_nuevo_plan", clear_on_submit=True):
    st.subheader("➕ Crear Nuevo Plan")
    col1, col2, col3 = st.columns(3)
    
    with col1: nombre_plan = st.text_input("Nombre del Plan")
    with col2: duracion_meses = st.number_input("Duración en Meses", min_value=1, value=1)
    with col3: precio_plan = st.number_input("Precio ($)", min_value=0.0, step=500.0)
        
    if st.form_submit_button("Guardar Nuevo Plan"):
        if nombre_plan:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Planes (NombrePlan, DuracionMeses, Precio) VALUES (?, ?, ?)",
                           (nombre_plan, int(duracion_meses), float(precio_plan)))
            conn.commit()
            st.success("¡Plan creado!")
            st.rerun()
        else:
            st.error("El nombre no puede estar vacío.")

st.divider()

# --- 2. LISTADO Y EDICIÓN ---
st.subheader("📋 Planes Configurables")

if not df_planes.empty:
    # Mostramos listado formateado
    df_mostrar = df_planes.copy()
    df_mostrar['Precio'] = df_mostrar['Precio'].map('${:,.2f}'.format)
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

    st.subheader("✏️ Modificar o Eliminar Plan")
    opciones_planes = df_planes.apply(lambda row: f"{row['IdPlan']} - {row['NombrePlan']}", axis=1).tolist()
    plan_seleccionado = st.selectbox("Seleccionar:", opciones_planes)
    
    id_plan_sel = int(plan_seleccionado.split(" - ")[0])
    datos_plan = df_planes[df_planes['IdPlan'] == id_plan_sel].iloc[0]
    
    col_edit, col_del = st.columns(2)
    
    with col_edit:
        with st.form("form_editar_plan"):
            st.write("⚙️ **Editar Valores**")
            nuevo_nombre = st.text_input("Nombre", value=datos_plan['NombrePlan'])
            nueva_duracion = st.number_input("Meses", value=int(datos_plan['DuracionMeses']))
            nuevo_precio = st.number_input("Precio ($)", value=float(datos_plan['Precio']))
            
            if st.form_submit_button("Actualizar"):
                cursor = conn.cursor()
                cursor.execute("UPDATE Planes SET NombrePlan=?, DuracionMeses=?, Precio=? WHERE IdPlan=?",
                               (nuevo_nombre, int(nueva_duracion), float(nuevo_precio), id_plan_sel))
                conn.commit()
                st.rerun()
                
    with col_del:
        if st.button("🗑️ Eliminar este plan", type="primary"):
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Planes WHERE IdPlan=?", (id_plan_sel,))
                conn.commit()
                st.rerun()
            except:
                st.error("No se puede eliminar: socios activos lo están usando.")
else:
    st.info("No hay planes cargados.")
