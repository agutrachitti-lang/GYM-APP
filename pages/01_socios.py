import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from database.conexion import get_connection

st.set_page_config(page_title="Gestión de Socios", layout="wide")
st.title("Socios del Gimnasio")

conn = get_connection()

try:
    conn.execute("CREATE TABLE IF NOT EXISTS Planes (IdPlan INTEGER PRIMARY KEY AUTOINCREMENT, NombrePlan TEXT, DuracionMeses INTEGER, Precio REAL)")
    conn.execute("CREATE TABLE IF NOT EXISTS Socios (IdSocio INTEGER PRIMARY KEY AUTOINCREMENT, Nombre TEXT, Apellido TEXT, DNI TEXT UNIQUE, IdPlan INTEGER, FechaAlta TEXT, FechaVencimiento TEXT, Saldo REAL, Activo INTEGER DEFAULT 1)")
    conn.commit()
except Exception as e:
    st.error(f"Error al crear tablas: {e}")

# --- CONTROL DEL ESTADO DEL EDITOR Y RESETEO DE ALTA ---
if "mostrar_editor" not in st.session_state:
    st.session_state.mostrar_editor = False
if "id_socio_a_editar" not in st.session_state:
    st.session_state.id_socio_a_editar = None
if "alta_key" not in st.session_state:
    st.session_state.alta_key = 0

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
        # Usamos una key dinámica que cambia cuando guardamos para vaciar los campos
        nombre = st.text_input("Nombre", key=f"alta_nom_{st.session_state.alta_key}")
        apellido = st.text_input("Apellido", key=f"alta_ape_{st.session_state.alta_key}")
    with col2:
        dni = st.text_input("DNI", key=f"alta_dni_{st.session_state.alta_key}")
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
            
            # --- SOLUCIÓN BALA DE PLATA PARA EL ID ---
            # Buscamos el ID más alto y le sumamos 1 manualmente
            cursor.execute("SELECT MAX(IdSocio) FROM Socios")
            max_id = cursor.fetchone()[0]
            nuevo_id = 1 if max_id is None else max_id + 1
            
            # Insertamos usando el nuevo_id generado
            cursor.execute("INSERT INTO Socios (IdSocio, Nombre, Apellido, DNI, IdPlan, FechaAlta, FechaVencimiento, Saldo, Activo) VALUES (?,?,?,?,?,?,?,?,1)",
                           (nuevo_id, nombre.strip().title(), apellido.strip().title(), dni, dict_planes[plan_elegido]['IdPlan'], fecha_alta.strftime('%Y-%m-%d'), fecha_vencimiento.strftime('%Y-%m-%d'), -float(dict_planes[plan_elegido]['Precio'])))
            conn.commit()
            
            # Sumamos 1 a la key, lo que resetea todos los campos de texto sin romper Streamlit
            st.session_state.alta_key += 1
            st.success("Socio guardado correctamente.")
            st.rerun()
        else:
            st.error("Completá Nombre, Apellido y DNI.")

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
    
    # --- ESCUDO CONTRA EL ERROR 'nan' ---
    # Forzamos a que cualquier ID roto (None/NaN) se convierta en un 0. Así podés seleccionarlo y borrarlo.
    df_socios['IdSocio'] = pd.to_numeric(df_socios['IdSocio'], errors='coerce').fillna(0).astype(int)
    
    mostrar_saldos = st.toggle("👁️ Mostrar saldos", value=False)
    df_tabla = df_socios.copy()
    
    # Aseguramos los formatos
    df_tabla['Estado'] = df_tabla['Activo'].apply(lambda x: '🟢 Activo' if str(x).strip() in ['1', '1.0'] else '🔴 Inactivo')
    df_tabla['Al Día'] = df_tabla['Saldo'].apply(lambda x: 'Sí' if float(x) >= 0 else 'No')
    df_tabla['Saldo_Display'] = df_tabla['Saldo'].apply(lambda x: f"${float(x):,.2f}" if mostrar_saldos else "******")
    
    # Reordenamos para que IdSocio sea la primera columna visible y eliminamos las técnicas
    columnas_finales = ['IdSocio', 'Nombre', 'Apellido', 'DNI', 'NombrePlan', 'FechaAlta', 'FechaVencimiento', 'Estado', 'Al Día', 'Saldo_Display']
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
if st.session_state.mostrar_editor and st.session_state.id_socio_a_editar is not None:
    # Filtramos con seguridad por si no encuentra el ID
    socios_filtrados = df_socios[df_socios['IdSocio'] == st.session_state.id_socio_a_editar]
    
    if not socios_filtrados.empty:
        s = socios_filtrados.iloc[0]
        st.write("---")
        st.info(f"⚙️ Editando a: {s['Nombre']} {s['Apellido']}")
        
        col_e, col_d = st.columns(2)
        with col_e:
            with st.form("form_editar"):
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
    else:
        st.error("Socio no encontrado. Por favor, recargá la página.")
        st.session_state.mostrar_editor = False
