import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from database.conexion import get_connection

st.set_page_config(page_title="Gestión de Socios", layout="wide")
st.title("Socios del Gimnasio")

conn = get_connection()

# --- CONTROL DEL ESTADO DEL EDITOR ---
if "mostrar_editor" not in st.session_state:
    st.session_state.mostrar_editor = False
if "id_socio_a_editar" not in st.session_state:
    st.session_state.id_socio_a_editar = None

# --- TRAER LOS PLANES ---
try:
    df_planes = pd.read_sql("SELECT IdPlan, NombrePlan, DuracionMeses, Precio FROM Planes", conn)
    dict_planes = {row['NombrePlan']: row for index, row in df_planes.iterrows()}
except:
    dict_planes = {}

# ==========================================
# 1. FORMULARIO DE ALTA (Sin st.form para que sea dinámico)
# ==========================================
with st.container(border=True):
    st.subheader("Agregar Nuevo Socio")
    col1, col2 = st.columns(2)
    with col1:
        # Usamos keys para poder limpiar los campos después de guardar
        nombre = st.text_input("Nombre", key="alta_nom")
        apellido = st.text_input("Apellido", key="alta_ape")
    with col2:
        dni = st.text_input("DNI", key="alta_dni")
        plan_elegido = st.selectbox("Seleccionar Plan", list(dict_planes.keys()) if dict_planes else ["Sin planes"])
    
    fecha_alta = st.date_input("Fecha de Inicio / Pago", value=datetime.today().date())
    
    # Al no estar en un form, esto se actualiza en tiempo real al cambiar el plan
    if dict_planes and plan_elegido in dict_planes:
        meses = int(dict_planes[plan_elegido]['DuracionMeses'])
        fecha_vencimiento = fecha_alta + relativedelta(months=meses)
        st.info(f"💰 Precio: ${dict_planes[plan_elegido]['Precio']:,.2f} | 📅 Vence el: {fecha_vencimiento.strftime('%d/%m/%Y')}")

    if st.button("Guardar Socio", type="primary"):
        if nombre and apellido and dni and dict_planes:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Socios (Nombre, Apellido, DNI, IdPlan, FechaAlta, FechaVencimiento, Saldo, Activo) VALUES (?,?,?,?,?,?,?,1)",
                           (nombre.strip().title(), apellido.strip().title(), dni, dict_planes[plan_elegido]['IdPlan'], fecha_alta.strftime('%Y-%m-%d'), fecha_vencimiento.strftime('%Y-%m-%d'), -float(dict_planes[plan_elegido]['Precio'])))
            conn.commit()
            
            # Limpiamos los campos visuales reseteando el session_state
            st.session_state['alta_nom'] = ""
            st.session_state['alta_ape'] = ""
            st.session_state['alta_dni'] = ""
            
            st.rerun()

st.divider()

# ==========================================
# 2. LISTADO DE SOCIOS
# ==========================================
st.subheader("Listado Actual")
try:
    df_socios = pd.read_sql("SELECT S.*, P.NombrePlan FROM Socios S LEFT JOIN Planes P ON S.IdPlan = P.IdPlan", conn)
except:
    df_socios = pd.DataFrame()

if not df_socios.empty:
    mostrar_saldos = st.toggle("👁️ Mostrar saldos", value=False)
    df_tabla = df_socios.copy()
    
    # Aseguramos los formatos
    df_tabla['Estado'] = df_tabla['Activo'].apply(lambda x: '🟢 Activo' if str(x).strip() in ['1', '1.0'] else '🔴 Inactivo')
    df_tabla['Al Día'] = df_tabla['Saldo'].apply(lambda x: 'Sí' if float(x) >= 0 else 'No')
    df_tabla['Saldo_Display'] = df_tabla['Saldo'].apply(lambda x: f"${float(x):,.2f}" if mostrar_saldos else "******")
    
    # Reordenamos para que IdSocio sea la primera columna visible y eliminamos las técnicas
    columnas_finales = ['IdSocio', 'Nombre', 'Apellido', 'DNI', 'NombrePlan', 'FechaAlta', 'FechaVencimiento', 'Estado', 'Al Día', 'Saldo_Display']
    # Filtramos por las columnas que realmente existen (por seguridad)
    columnas_finales = [col for col in columnas_finales if col in df_tabla.columns]
    
    st.dataframe(df_tabla[columnas_finales].rename(columns={'Saldo_Display': 'Saldo'}), use_container_width=True, hide_index=True)

    # --- SELECCIÓN Y BOTÓN DE GESTIÓN ---
    st.write("---")
    opciones = df_socios.apply(lambda r: f"{r['IdSocio']} - {r['Nombre']} {r['Apellido']}", axis=1).tolist()
    socio_sel = st.selectbox("Seleccionar para gestionar:", opciones, key="sel_gestionar")
    
    if st.button("🔧 Modificar / Eliminar seleccionado", type="primary"):
        st.session_state.mostrar_editor = True
        st.session_state.id_socio_a_editar = int(socio_sel.split(" - ")[0])
        st.rerun()
else:
    st.info("No hay socios registrados.")

# ==========================================
# 3. PANEL DE EDICIÓN
# ==========================================
if st.session_state.mostrar_editor and st.session_state.id_socio_a_editar:
    s = df_socios[df_socios['IdSocio'] == st.session_state.id_socio_a_editar].iloc[0]
    st.write("---")
    st.info(f"⚙️ Editando a: {s['Nombre']} {s['Apellido']}")
    
    col_e, col_d = st.columns(2)
    with col_e:
        with st.form("form_editar"):
            # Lógica robusta: etiqueta estática para que Streamlit no pierda el valor al destildar
            es_activo = True if str(s['Activo']).strip() in ['1', '1.0'] else False
            nuevo_estado = st.checkbox("🟢 Mantener como Socio Activo (Destildar para Inactivo)", value=es_activo)
            
            n = st.text_input("Nombre", value=s['Nombre'])
            a = st.text_input("Apellido", value=s['Apellido'])
            d = st.text_input("DNI", value=s['DNI'])
            
            lista_nombres_planes = list(dict_planes.keys()) if dict_planes else ["Sin planes"]
            nombre_plan_actual = s.get('NombrePlan', '')
            index_plan = lista_nombres_planes.index(nombre_plan_actual) if nombre_plan_actual in lista_nombres_planes else 0
            nuevo_plan = st.selectbox("Plan", lista_nombres_planes, index=index_plan)
            
            sald = st.number_input("Saldo", value=float(s['Saldo']))
            
            if st.form_submit_button("Guardar Cambios"):
                estado_bit = 1 if nuevo_estado else 0
                nuevo_id_plan = int(dict_planes[nuevo_plan]['IdPlan']) if dict_planes else s['IdPlan']
                
                cursor = conn.cursor()
                cursor.execute("UPDATE Socios SET Nombre=?, Apellido=?, DNI=?, IdPlan=?, Saldo=?, Activo=? WHERE IdSocio=?", 
                               (n, a, d, nuevo_id_plan, sald, estado_bit, int(s['IdSocio'])))
                conn.commit()
                st.session_state.mostrar_editor = False
                st.rerun()
                
    with col_d:
        with st.expander("🗑️ Eliminar Socio Definitivamente"):
            st.warning("¿Estás seguro? Esta acción borrará al socio del sistema.")
            if st.button("Sí, borrar socio", type="primary"):
                conn.cursor().execute("DELETE FROM Socios WHERE IdSocio=?", (int(s['IdSocio']),))
                conn.commit()
                st.session_state.mostrar_editor = False
                st.rerun()
                
        if st.button("❌ Cancelar / Cerrar Editor"):
            st.session_state.mostrar_editor = False
            st.rerun()
