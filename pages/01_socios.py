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
# 1. FORMULARIO DE ALTA
# ==========================================
with st.form("form_nuevo_socio", clear_on_submit=True):
    st.subheader("Agregar Nuevo Socio")
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
    with col2:
        dni = st.text_input("DNI")
        plan_elegido = st.selectbox("Seleccionar Plan", list(dict_planes.keys()) if dict_planes else ["Sin planes"])
    
    fecha_alta = st.date_input("Fecha de Inicio / Pago", value=datetime.today().date())
    
    if dict_planes and plan_elegido in dict_planes:
        meses = int(dict_planes[plan_elegido]['DuracionMeses'])
        fecha_vencimiento = fecha_alta + relativedelta(months=meses)
        st.info(f"💰 Precio: ${dict_planes[plan_elegido]['Precio']:,.2f} | 📅 Vence el: {fecha_vencimiento.strftime('%d/%m/%Y')}")

    if st.form_submit_button("Guardar Socio"):
        if nombre and apellido and dni and dict_planes:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Socios (Nombre, Apellido, DNI, IdPlan, FechaAlta, FechaVencimiento, Saldo, Activo) VALUES (?,?,?,?,?,?,?,1)",
                           (nombre.strip().title(), apellido.strip().title(), dni, dict_planes[plan_elegido]['IdPlan'], fecha_alta, fecha_vencimiento, -float(dict_planes[plan_elegido]['Precio'])))
            conn.commit()
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
    
    df_tabla['Estado'] = df_tabla['Activo'].apply(lambda x: '🟢 Activo' if x == 1 else '🔴 Inactivo')
    df_tabla['Al Día'] = df_tabla['Saldo'].apply(lambda x: 'Sí' if float(x) >= 0 else 'No')
    df_tabla['Saldo'] = df_tabla['Saldo'].apply(lambda x: f"${float(x):,.2f}" if mostrar_saldos else "******")
    
    st.dataframe(df_tabla.drop(columns=['Activo', 'IdPlan'], errors='ignore'), use_container_width=True, hide_index=True)

    # --- SELECCIÓN Y BOTÓN ---
    opciones = df_socios.apply(lambda r: f"{r['IdSocio']} - {r['Nombre']} {r['Apellido']}", axis=1).tolist()
    socio_sel = st.selectbox("Seleccionar para gestionar:", opciones, key="sel_gestionar")
    
    if st.button("🔧 Modificar / Eliminar", type="primary"):
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
            n = st.text_input("Nombre", value=s['Nombre'])
            a = st.text_input("Apellido", value=s['Apellido'])
            d = st.text_input("DNI", value=s['DNI'])
            sald = st.number_input("Saldo", value=float(s['Saldo']))
            if st.form_submit_button("Guardar Cambios"):
                cursor = conn.cursor()
                cursor.execute("UPDATE Socios SET Nombre=?, Apellido=?, DNI=?, Saldo=? WHERE IdSocio=?", (n, a, d, sald, s['IdSocio']))
                conn.commit()
                st.session_state.mostrar_editor = False
                st.rerun()
    with col_d:
        if st.button("🗑️ Eliminar Socio Definitivamente"):
            conn.cursor().execute("DELETE FROM Socios WHERE IdSocio=?", (s['IdSocio'],))
            conn.commit()
            st.session_state.mostrar_editor = False
            st.rerun()
            
    # Botón de cierre añadido
    if st.button("❌ Cancelar / Cerrar Editor"):
        st.session_state.mostrar_editor = False
        st.rerun()
