import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from database.conexion import get_connection

st.set_page_config(page_title="Gestión de Socios", layout="wide")
st.title("Socios del Gimnasio")

conn = get_connection()

# --- ESTADO DEL EDITOR ---
if "mostrar_editor" not in st.session_state:
    st.session_state.mostrar_editor = False
if "id_socio_a_editar" not in st.session_state:
    st.session_state.id_socio_a_editar = None

# --- CARGA DE DATOS ---
try:
    df_planes = pd.read_sql("SELECT * FROM Planes", conn)
    dict_planes = {row['NombrePlan']: row for index, row in df_planes.iterrows()}
    query_select = "SELECT S.*, P.NombrePlan FROM Socios S LEFT JOIN Planes P ON S.IdPlan = P.IdPlan"
    df_socios = pd.read_sql(query_select, conn)
except:
    df_planes = pd.DataFrame()
    dict_planes = {}
    df_socios = pd.DataFrame()

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
    
    fecha_alta = st.date_input("Fecha de Inicio", value=datetime.today().date())
    
    if dict_planes and plan_elegido in dict_planes:
        meses = int(dict_planes[plan_elegido]['DuracionMeses'])
        fecha_venc = fecha_alta + relativedelta(months=meses)
        st.info(f"Vence el: {fecha_venc.strftime('%d/%m/%Y')}")

    if st.form_submit_button("Guardar Socio"):
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Socios (Nombre, Apellido, DNI, IdPlan, FechaAlta, FechaVencimiento, Saldo, Activo) VALUES (?,?,?,?,?,?,?,1)",
                       (nombre.title(), apellido.title(), dni, dict_planes[plan_elegido]['IdPlan'], fecha_alta, fecha_venc, -float(dict_planes[plan_elegido]['Precio'])))
        conn.commit()
        st.rerun()

st.divider()

# ==========================================
# 2. LISTADO Y GESTIÓN (UNIFICADO)
# ==========================================
st.subheader("Listado Actual")

if not df_socios.empty:
    # Búsqueda
    busqueda = st.text_input("🔍 Buscar socio:").lower()
    df_mostrar = df_socios[df_socios.apply(lambda r: busqueda in str(r['Nombre']).lower() or busqueda in str(r['Apellido']).lower() or busqueda in str(r['DNI']), axis=1)]
    
    # Tabla
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

    # Selección única
    st.write("---")
    opciones = df_mostrar.apply(lambda r: f"{r['IdSocio']} - {r['Nombre']} {r['Apellido']}", axis=1).tolist()
    socio_sel = st.selectbox("Seleccionar para gestionar:", opciones)
    
    if st.button("🔧 Modificar / Eliminar", type="primary"):
        st.session_state.mostrar_editor = True
        st.session_state.id_socio_a_editar = int(socio_sel.split(" - ")[0])
        st.rerun()
else:
    st.info("No hay socios registrados.")
