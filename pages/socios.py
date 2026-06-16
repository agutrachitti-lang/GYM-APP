import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from database.conexion import get_connection

st.set_page_config(page_title="Gestión de Socios", layout="wide")
st.title("Socios del Gimnasio")

conn = get_connection()

# --- ESTADOS DE SESIÓN ---
if "mostrar_editor" not in st.session_state:
    st.session_state.mostrar_editor = False
if "id_socio_a_editar" not in st.session_state:
    st.session_state.id_socio_a_editar = None

# --- CARGA SEGURA DE PLANES ---
try:
    df_planes = pd.read_sql("SELECT IdPlan, NombrePlan, DuracionMeses, Precio FROM Planes", conn)
except:
    df_planes = pd.DataFrame(columns=['IdPlan', 'NombrePlan', 'DuracionMeses', 'Precio'])

dict_planes = {row['NombrePlan']: row for index, row in df_planes.iterrows()} if not df_planes.empty else {}

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

    if plan_elegido != "Sin planes" and plan_elegido in dict_planes:
        meses_a_sumar = int(dict_planes[plan_elegido].get('DuracionMeses', 1))
        precio = float(dict_planes[plan_elegido].get('Precio', 0))
        fecha_vencimiento = fecha_alta + relativedelta(months=meses_a_sumar)
        st.info(f"💰 Precio: ${precio:.2f} | 📅 Vence: {fecha_vencimiento.strftime('%d/%m/%Y')}")
    else:
        meses_a_sumar = 1
        precio = 0
        fecha_vencimiento = fecha_alta

    btn_guardar = st.form_submit_button("Guardar Socio")

    if btn_guardar:
        if nombre and apellido and dni and plan_elegido != "Sin planes":
            try:
                cursor = conn.cursor()
                query_insert = """
                    INSERT INTO Socios (Nombre, Apellido, DNI, IdPlan, FechaAlta, FechaVencimiento, Saldo, Activo) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """
                cursor.execute(query_insert, (nombre.title(), apellido.title(), dni, int(dict_planes[plan_elegido]['IdPlan']), fecha_alta, fecha_vencimiento, -precio))
                conn.commit()
                st.success("Socio registrado.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
        else:
            st.error("Completa todos los campos.")

st.divider()

# ==========================================
# 2. LISTADO DE SOCIOS
# ==========================================
st.subheader("Listado Actual")

try:
    query_select = """
        SELECT S.IdSocio, S.Nombre, S.Apellido, S.DNI, P.NombrePlan, S.FechaAlta, S.FechaVencimiento, S.Activo, S.Saldo 
        FROM Socios S
        LEFT JOIN Planes P ON S.IdPlan = P.IdPlan
    """
    df_socios = pd.read_sql(query_select, conn)
except:
    df_socios = pd.DataFrame()

if not df_socios.empty:
    # (Tu lógica de filtrado y visualización...)
    st.dataframe(df_socios, use_container_width=True)
else:
    st.info("No hay socios registrados aún.")
