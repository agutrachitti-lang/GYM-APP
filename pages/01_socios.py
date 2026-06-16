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

# --- TRAER LOS PLANES (CON PROTECCIÓN SI LA TABLA ESTÁ VACÍA) ---
try:
    query_planes = "SELECT IdPlan, NombrePlan, DuracionMeses, Precio FROM Planes"
    df_planes = pd.read_sql(query_planes, conn)
    dict_planes = {row['NombrePlan']: row for index, row in df_planes.iterrows()}
except:
    st.warning("⚠️ No se encontraron planes. Cargalos en la sección de Planes primero.")
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
        # Si no hay planes, ponemos un placeholder
        plan_list = list(dict_planes.keys()) if dict_planes else ["Sin planes disponibles"]
        plan_elegido = st.selectbox("Seleccionar Plan", plan_list)
    
    fecha_alta = st.date_input("Fecha de Inicio / Pago", value=datetime.today().date())
    
    # Lógica de cálculo de vencimiento segura
    if dict_planes and plan_elegido in dict_planes:
        meses_a_sumar = int(dict_planes[plan_elegido]['DuracionMeses'])
        precio_plan = float(dict_planes[plan_elegido]['Precio'])
        fecha_vencimiento = fecha_alta + relativedelta(months=meses_a_sumar)
        st.info(f"💰 Precio del Plan: ${precio_plan:,.2f} | 📅 Vence el: {fecha_vencimiento.strftime('%d/%m/%Y')}")
    else:
        fecha_vencimiento = fecha_alta
        precio_plan = 0.0

    btn_guardar = st.form_submit_button("Guardar Socio")
    
    if btn_guardar:
        if nombre and apellido and dni and dict_planes:
            try:
                cursor = conn.cursor()
                id_plan = int(dict_planes[plan_elegido]['IdPlan'])
                saldo_inicial = -precio_plan 
                
                # INSERT (Aseguramos que las columnas coincidan con la base de datos)
                query_insert = """
                    INSERT INTO Socios (Nombre, Apellido, DNI, IdPlan, FechaAlta, FechaVencimiento, Saldo, Activo) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """
                cursor.execute(query_insert, (nombre.strip().title(), apellido.strip().title(), dni, id_plan, fecha_alta.strftime('%Y-%m-%d'), fecha_vencimiento.strftime('%Y-%m-%d'), saldo_inicial))
                conn.commit()
                st.success("¡Socio registrado con éxito!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: Verificá si el DNI ya existe o si faltan columnas en la BD.")
        elif not dict_planes:
            st.error("No se puede guardar sin un plan configurado.")
        else:
            st.error("Completá todos los campos.")

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
    df_tabla = df_socios.copy()
    
    # Toggle de saldos
    mostrar_saldos = st.toggle("👁️ Mostrar saldos", value=False)
    
    df_tabla['Estado'] = df_tabla['Activo'].apply(lambda x: '🟢 Activo' if x == 1 else '🔴 Inactivo')
    df_tabla['Al Día'] = df_tabla['Saldo'].apply(lambda x: 'Sí' if x >= 0 else 'No')

    if not mostrar_saldos:
        df_tabla['Saldo'] = "******"
    else:
        df_tabla['Saldo'] = df_tabla['Saldo'].map('${:,.2f}'.format)

    st.dataframe(df_tabla.drop(columns=['Activo']), use_container_width=True, hide_index=True)

    # --- SELECCIÓN PARA EDITAR ---
    opciones_socios = df_socios.apply(lambda row: f"{row['IdSocio']} - {row['Nombre']} {row['Apellido']}", axis=1).tolist()
    socio_sel = st.selectbox("Gestionar socio:", opciones_socios)
    id_seleccionado = int(socio_sel.split(" - ")[0])

    if st.button("🔧 Modificar / Eliminar"):
        st.session_state.mostrar_editor = True
        st.session_state.id_socio_a_editar = id_seleccionado
        st.rerun()
else:
    st.info("No hay socios registrados aún.")

# ==========================================
# 3. SELECCIÓN Y BOTÓN DE APERTURA (REEMPLAZAR ESTO)
# ==========================================
if not df_mostrar.empty:
    st.write("---")
    # Usamos una sola columna para el selectbox y el botón
    col_sel, col_btn = st.columns([3, 1])
    
    with col_sel:
        # Creamos una lista de opciones clara
        lista_opciones = df_mostrar.apply(
            lambda x: f"{x['IdSocio']} - {x['Nombre']} {x['Apellido']}", axis=1
        ).tolist()
        socio_sel = st.selectbox("Seleccionar socio para gestionar:", lista_opciones)
    
    with col_btn:
        st.write("") # Espacio para alinear
        st.write("") 
        # IMPORTANTE: Este botón está fuera de cualquier form
        if st.button("🔧 Modificar / Eliminar", type="primary", use_container_width=True):
            id_seleccionado = int(socio_sel.split(" - ")[0])
            st.session_state.mostrar_editor = True
            st.session_state.id_socio_a_editar = id_seleccionado
            st.rerun()
