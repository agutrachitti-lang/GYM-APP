import streamlit as st
import pandas as pd
from database.conexion import get_connection

st.set_page_config(page_title="Gestión de Planes", layout="wide")
st.title("Configuración de Planes y Precios")

conn = get_connection()

# --- 1. FORMULARIO PARA CREAR UN PLAN NUEVO ---
with st.form("form_nuevo_plan", clear_on_submit=True):
    st.subheader("➕ Crear Nuevo Plan")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nombre_plan = st.text_input("Nombre del Plan (Ej: Pase Libre Mensual)")
    with col2:
        duracion_meses = st.number_input("Duración en Meses", min_value=1, max_value=24, value=1)
    with col3:
        precio_plan = st.number_input("Precio ($)", min_value=0.0, step=500.0, value=10000.0)
        
    btn_guardar_plan = st.form_submit_button("Guardar Nuevo Plan")
    
    if btn_guardar_plan:
        if nombre_plan:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Planes (NombrePlan, DuracionMeses, Precio) VALUES (?, ?, ?)",
                (nombre_plan, int(duracion_meses), float(precio_plan))
            )
            conn.commit()
            st.success(f"¡Plan '{nombre_plan}' creado con éxito!")
            st.rerun()
        else:
            st.error("El nombre del plan no puede estar vacío.")

st.divider()

# --- 2. LISTADO ACTUAL DE PLANES ---
st.subheader("📋 Planes Configurables en el Sistema")
query_planes = "SELECT IdPlan, NombrePlan, DuracionMeses, Precio FROM Planes"
df_planes = pd.read_sql(query_planes, conn)

# Formateamos la columna de precio para que se vea con el signo $
df_mostrar = df_planes.copy()
df_mostrar['Precio'] = df_mostrar['Precio'].map('${:,.2f}'.format)
st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

st.divider()

# --- 3. MODIFICAR O ELIMINAR PLANES EXISTENTES ---
if not df_planes.empty:
    st.subheader("✏️ Modificar o Eliminar Plan Existente")
    
    # Armamos la lista para seleccionar
    opciones_planes = df_planes.apply(lambda row: f"{row['IdPlan']} - {row['NombrePlan']}", axis=1).tolist()
    plan_seleccionado = st.selectbox("Seleccionar Plan para editar o borrar:", opciones_planes)
    
    id_plan_sel = int(plan_seleccionado.split(" - ")[0])
    datos_plan = df_planes[df_planes['IdPlan'] == id_plan_sel].iloc[0]
    
    col_edit, col_del = st.columns(2)
    
    # Formulario de Edición de Valores
    with col_edit:
        with st.form("form_editar_plan"):
            st.write("⚙️ **Editar Valores**")
            nuevo_nombre = st.text_input("Nombre del Plan", value=datos_plan['NombrePlan'])
            nueva_duracion = st.number_input("Duración (Meses)", min_value=1, max_value=24, value=int(datos_plan['DuracionMeses']))
            nuevo_precio = st.number_input("Precio ($)", min_value=0.0, step=500.0, value=float(datos_plan['Precio']))
            
            btn_actualizar_plan = st.form_submit_button("Actualizar Valores")
            
            if btn_actualizar_plan:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Planes SET NombrePlan=?, DuracionMeses=?, Precio=? WHERE IdPlan=?",
                    (nuevo_nombre, int(nueva_duracion), float(nuevo_precio), id_plan_sel)
                )
                conn.commit()
                st.success("¡Valores actualizados correctamente!")
                st.rerun()
                
    # Formulario de Baja de Plan
    with col_del:
        with st.form("form_eliminar_plan"):
            st.write("🗑️ **Dar de Baja Plan**")
            st.warning(f"Se eliminará el plan: {datos_plan['NombrePlan']}. Esto no afectará a los socios que ya lo tengan asignado históricamente, pero no podrá seleccionarse para nuevos socios.")
            btn_eliminar_plan = st.form_submit_button("Confirmar Eliminación")
            
            if btn_eliminar_plan:
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Planes WHERE IdPlan=?", (id_plan_sel,))
                    conn.commit()
                    st.error("Plan eliminado del sistema.")
                    st.rerun()
                except Exception as e:
                    st.error("No se puede eliminar este plan porque hay socios activos que lo están usando actualmente. Modificá primero a esos socios antes de borrar el plan.")