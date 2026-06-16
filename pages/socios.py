import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from database.conexion import get_connection

st.set_page_config(page_title="Gestión de Socios", layout="wide")
st.title("Socios del Gimnasio")

conn = get_connection()

# --- COMIENZO: CONTROL DEL ESTADO DEL EDITOR ---
if "mostrar_editor" not in st.session_state:
    st.session_state.mostrar_editor = False
if "id_socio_a_editar" not in st.session_state:
    st.session_state.id_socio_a_editar = None

# --- TRAER LOS PLANES DISPONIBLES DESDE SQL ---
query_planes = "SELECT IdPlan, NombrePlan, DuracionMeses, Precio FROM Planes"
df_planes = pd.read_sql(query_planes, conn)
dict_planes = {row['NombrePlan']: row for index, row in df_planes.iterrows()}

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
        plan_elegido = st.selectbox("Seleccionar Plan", list(dict_planes.keys()))
    
    fecha_alta = st.date_input("Fecha de Inicio / Pago", value=datetime.today().date())
    
    meses_a_sumar = dict_planes[plan_elegido]['DuracionMeses']
    fecha_vencimiento = fecha_alta + relativedelta(months=meses_a_sumar)
    
    st.info(f"💰 Precio del Plan: ${dict_planes[plan_elegido]['Precio']:.2f} | 📅 Vence automáticamente el: {fecha_vencimiento.strftime('%d/%m/%Y')}")
    
    btn_guardar = st.form_submit_button("Guardar Socio")
    
    if btn_guardar:
        if nombre and apellido and dni:
            nombre_limpio = nombre.strip().title()
            apellido_limpio = apellido.strip().title()
            
            try:
                cursor = conn.cursor()
                id_plan = int(dict_planes[plan_elegido]['IdPlan'])
                
                precio_plan = float(dict_planes[plan_elegido]['Precio'])
                saldo_inicial = -precio_plan 
                
                query_insert = """
                    INSERT INTO Socios (Nombre, Apellido, DNI, IdPlan, FechaAlta, FechaVencimiento, Saldo) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(query_insert, (nombre_limpio, apellido_limpio, dni, id_plan, fecha_alta, fecha_vencimiento, saldo_inicial))
                conn.commit()
                st.success(f"¡{nombre_limpio} {apellido_limpio} registrado! Deuda de cuota generada correctamente.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: Asegurate de que el DNI no esté duplicado.")
        else:
            st.error("Por favor completa todos los campos obligatorios.")

st.divider()

# ==========================================
# 2. LISTADO DE SOCIOS CON BUSCADOR
# ==========================================
st.subheader("Listado Actual")

# 1. Primero hacemos la consulta a la base de datos
query_select = """
    SELECT S.IdSocio, S.Nombre, S.Apellido, S.DNI, P.NombrePlan, S.FechaAlta, S.FechaVencimiento, S.Activo, S.Saldo 
    FROM Socios S
    INNER JOIN Planes P ON S.IdPlan = P.IdPlan
"""
df_socios = pd.read_sql(query_select, conn)

# 2. Ahora que ya tenemos df_socios, podemos poner el botón de descarga
import io
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_socios.to_excel(writer, index=False, sheet_name='Socios')

st.download_button(
    label="📥 Descargar Listado a Excel",
    data=buffer,
    file_name="listado_socios.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 3. Seguimos con el resto de la lógica (buscador, toggle, etc.)
busqueda = st.text_input("🔍 Buscar socio por Nombre, Apellido o DNI:").strip().lower()

if busqueda:
    df_mostrar = df_socios[
        df_socios['Nombre'].str.lower().str.contains(busqueda) |
        df_socios['Apellido'].str.lower().str.contains(busqueda) |
        df_socios['DNI'].str.lower().str.contains(busqueda)
    ]
else:
    df_mostrar = df_socios

# ... (continúa con el código del toggle y el st.dataframe)

# ... (después del query_select y el filtro de búsqueda) ...

df_tabla = df_mostrar.copy()

# Switch para ocultar saldos sensibles
mostrar_saldos = st.toggle("👁️ Mostrar/Ocultar saldos", value=False)

df_tabla['Estado'] = df_tabla['Activo'].apply(lambda x: '🟢 Activo' if x else '🔴 Inactivo')
df_tabla['Al Día'] = df_tabla['Saldo'].apply(lambda x: 'Sí' if float(x) >= 0 else 'No')

# Si el switch está apagado, ocultamos la columna o ponemos asteriscos
if not mostrar_saldos:
    df_tabla['Saldo'] = "******"
else:
    df_tabla['Saldo'] = df_tabla['Saldo'].map('${:,.2f}'.format)

df_tabla = df_tabla.drop(columns=['Activo'])
st.dataframe(df_tabla, use_container_width=True, hide_index=True)

# ==========================================
# 3. SELECCIÓN Y BOTÓN DE APERTURA
# ==========================================
if not df_mostrar.empty:
    st.write("")
    col_sel, col_btn = st.columns([3, 1])
    
    with col_sel:
        opciones_socios = df_mostrar.apply(lambda row: f"{row['IdSocio']} - {row['Nombre']} {row['Apellido']}", axis=1).tolist()
        socio_sel = st.selectbox("Seleccionar socio del listado para gestionar:", opciones_socios, label_visibility="collapsed")
        id_seleccionado = int(socio_sel.split(" - ")[0])
    
    with col_btn:
        if st.button("🔧 Modificar / Eliminar", use_container_width=True):
            st.session_state.mostrar_editor = True
            st.session_state.id_socio_a_editar = id_seleccionado
            st.rerun()
else:
    st.session_state.mostrar_editor = False
    st.session_state.id_socio_a_editar = None

# ==========================================
# 4. PANEL CONDICIONAL: MODIFICACIÓN Y BAJA
# ==========================================
if st.session_state.mostrar_editor and st.session_state.id_socio_a_editar:
    if st.session_state.id_socio_a_editar in df_socios['IdSocio'].values:
        datos_socio = df_socios[df_socios['IdSocio'] == st.session_state.id_socio_a_editar].iloc[0]
        
        st.write("")
        st.info(f"⚙️ Editando a: **{datos_socio['Nombre']} {datos_socio['Apellido']}** (ID: {datos_socio['IdSocio']})")
        
        col_edit, col_del = st.columns(2)
        
        # -- Formulario de Edición --
        with col_edit:
            with st.form("form_editar_socio"):
                st.write("✏️ **Editar Datos**")
                
                nuevo_estado = st.checkbox("🟢 Socio Activo", value=bool(datos_socio['Activo']))
                nuevo_nombre = st.text_input("Nombre", value=datos_socio['Nombre'])
                nuevo_apellido = st.text_input("Apellido", value=datos_socio['Apellido'])
                nuevo_dni = st.text_input("DNI", value=datos_socio['DNI'])
                
                lista_nombres_planes = list(dict_planes.keys())
                index_plan = lista_nombres_planes.index(datos_socio['NombrePlan']) if datos_socio['NombrePlan'] in lista_nombres_planes else 0
                nuevo_plan = st.selectbox("Plan", lista_nombres_planes, index=index_plan)
                
                nueva_fecha_venc = st.date_input("Vencimiento", value=pd.to_datetime(datos_socio['FechaVencimiento']).date())
                
                # NUEVO: Campo para modificar el saldo a mano
                nuevo_saldo = st.number_input("Saldo Actual ($)", value=float(datos_socio['Saldo']), step=500.0)
                
                btn_actualizar = st.form_submit_button("Actualizar")
                
                if btn_actualizar:
                    nombre_limpio = nuevo_nombre.strip().title()
                    apellido_limpio = nuevo_apellido.strip().title()
                    nuevo_id_plan = int(dict_planes[nuevo_plan]['IdPlan'])
                    estado_bit = 1 if nuevo_estado else 0
                    
                    cursor = conn.cursor()
                    # NUEVO: Agregamos Saldo=? en el SET y nuevo_saldo en el execute
                    query_update = """
                        UPDATE Socios 
                        SET Nombre=?, Apellido=?, DNI=?, IdPlan=?, FechaVencimiento=?, Activo=?, Saldo=?
                        WHERE IdSocio=?
                    """
                    cursor.execute(query_update, (nombre_limpio, apellido_limpio, nuevo_dni, nuevo_id_plan, nueva_fecha_venc, estado_bit, float(nuevo_saldo), st.session_state.id_socio_a_editar))
                    conn.commit()
                    
                    st.session_state.mostrar_editor = False
                    st.session_state.id_socio_a_editar = None
                    st.success("¡Socio actualizado con éxito!")
                    st.rerun()

        with col_del:
            with st.form("form_eliminar_socio"):
                st.write("🗑️ **Eliminar Socio**")
                st.warning(f"Se eliminará a {datos_socio['Nombre']} {datos_socio['Apellido']} permanentemente.")
                btn_eliminar = st.form_submit_button("Sí, Eliminar")
                
                if btn_eliminar:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Socios WHERE IdSocio=?", (st.session_state.id_socio_a_editar,))
                    conn.commit()
                    
                    st.session_state.mostrar_editor = False
                    st.session_state.id_socio_a_editar = None
                    st.error("Socio eliminado.")
                    st.rerun()
        
        if st.button("❌ Cancelar / Cerrar Editor"):
            st.session_state.mostrar_editor = False
            st.session_state.id_socio_a_editar = None
            st.rerun()