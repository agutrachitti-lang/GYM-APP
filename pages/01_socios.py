import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from database.conexion import get_connection

st.set_page_config(page_title="Gestión de Socios", layout="wide")
st.title("Socios del Gimnasio")

# --- CONEXIÓN A TURSO ---
url, token = get_connection()

def ejecutar_query(query, params=()):
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
    
    return response.json()

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
        for col in ['idsocio', 'dni', 'idplan', 'saldo', 'activo', 'duracionmeses', 'precio']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e:
        return pd.DataFrame()

# --- ESTADOS DE SESIÓN ---
if "mostrar_editor" not in st.session_state:
    st.session_state.mostrar_editor = False
if "id_socio_a_editar" not in st.session_state:
    st.session_state.id_socio_a_editar = None
if "alta_key" not in st.session_state:
    st.session_state.alta_key = 0

# --- CARGAR DATOS ---
df_socios = leer_tabla("SELECT S.*, P.NombrePlan FROM Socios S LEFT JOIN Planes P ON S.IdPlan = P.IdPlan")
df_planes = leer_tabla("SELECT * FROM Planes")

# ==========================================
# 1. FORMULARIO DE ALTA
# ==========================================
with st.container(border=True):
    st.subheader("Agregar Nuevo Socio")
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre", key=f"alta_nom_{st.session_state.alta_key}")
        apellido = st.text_input("Apellido", key=f"alta_ape_{st.session_state.alta_key}")
    with col2:
        dni = st.text_input("DNI", key=f"alta_dni_{st.session_state.alta_key}")
        lista_planes = df_planes['nombreplan'].tolist() if not df_planes.empty else ["Sin planes"]
        plan_elegido = st.selectbox("Seleccionar Plan", lista_planes, key=f"alta_plan_{st.session_state.alta_key}")
    
    fecha_alta = st.date_input("Fecha de Inicio / Pago", value=datetime.today().date())
    
    id_plan = None
    precio = 0.0
    fecha_vencimiento = fecha_alta
    
    if not df_planes.empty and plan_elegido != "Sin planes":
        plan_row = df_planes[df_planes['nombreplan'] == plan_elegido].iloc[0]
        id_plan = int(plan_row['idplan'])
        meses = int(plan_row['duracionmeses'])
        precio = float(plan_row['precio'])
        fecha_vencimiento = fecha_alta + relativedelta(months=meses)
        st.info(f"💰 Precio del Plan: ${precio:,.2f} | 📅 Vence automáticamente el: {fecha_vencimiento.strftime('%d/%m/%Y')}")

    if st.button("Guardar Socio"):
        if nombre and apellido and dni:
            
            # --- CONTROL DE DUPLICADOS EN PYTHON ---
            dni_limpio = str(dni).strip()
            ya_existe = False
            if not df_socios.empty:
                ya_existe = dni_limpio in df_socios['dni'].astype(str).str.strip().values
                
            if ya_existe:
                st.error("⚠️ El DNI ingresado ya pertenece a un socio registrado.")
            else:
                # --- SOLUCIÓN: DEJAMOS QUE TURSO ASIGNE EL ID AUTOINCREMENTAL ---
                res = ejecutar_query(
                    "INSERT INTO Socios (Nombre, Apellido, DNI, IdPlan, FechaAlta, FechaVencimiento, Saldo, Activo) VALUES (?,?,?,?,?,?,?,1)", 
                    [nombre.strip().title(), apellido.strip().title(), dni_limpio, id_plan, fecha_alta.strftime('%Y-%m-%d'), fecha_vencimiento.strftime('%Y-%m-%d'), -precio]
                )
                
                str_res = str(res).lower()
                if "error" in str_res or ("message" in res and "results" not in res):
                    st.error("⚠️ Error técnico al guardar en Turso:")
                    st.json(res)
                else:
                    st.session_state.alta_key += 1
                    st.success("Socio guardado exitosamente.")
                    st.rerun()
        else:
            st.error("Por favor completa los campos obligatorios.")

st.divider()

# ==========================================
# 2. LISTADO DE SOCIOS
# ==========================================
st.subheader("Listado Actual")
if not df_socios.empty:
    
    csv = df_socios.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
    st.download_button(label="📥 Descargar Listado a Excel", data=csv, file_name='socios_gym.csv', mime='text/csv')
    
    buscar = st.text_input("🔍 Buscar socio por Nombre, Apellido o DNI:")
    mostrar_saldos = st.toggle("👁️ Mostrar/Ocultar saldos", value=False)
    
    df_tabla = df_socios.copy()
    
    if buscar:
        mask = df_tabla.astype(str).apply(lambda x: x.str.contains(buscar, case=False)).any(axis=1)
        df_tabla = df_tabla[mask]
    
    df_tabla['Estado'] = df_tabla['activo'].apply(lambda x: '🟢 Activo' if str(x).strip() in ['1', '1.0'] else '🔴 Inactivo')
    df_tabla['Al Día'] = df_tabla['saldo'].apply(lambda x: 'Sí' if pd.notna(x) and float(x) >= 0 else 'No')
    df_tabla['Saldo_Display'] = df_tabla['saldo'].apply(lambda x: f"${float(x):,.2f}" if pd.notna(x) and mostrar_saldos else ("******" if pd.notna(x) else "$0.00"))
    
    rename_dict = {
        'idsocio': 'IdSocio', 'nombre': 'Nombre', 'apellido': 'Apellido', 'dni': 'DNI',
        'nombreplan': 'NombrePlan', 'fechaalta': 'FechaAlta', 'fechavencimiento': 'FechaVencimiento'
    }
    df_tabla = df_tabla.rename(columns=rename_dict)
    
    col_orden = ['IdSocio', 'Nombre', 'Apellido', 'DNI', 'NombrePlan', 'FechaAlta', 'FechaVencimiento', 'Saldo_Display', 'Estado', 'Al Día']
    col_orden = [c for c in col_orden if c in df_tabla.columns]
    
    st.dataframe(df_tabla[col_orden].rename(columns={'Saldo_Display': 'Saldo'}), use_container_width=True, hide_index=True)

    st.write("---")
    
    opciones_socios = df_socios.apply(
        lambda r: f"{int(r['idsocio']) if pd.notna(r['idsocio']) else 0} - {r['nombre']} {r['apellido']}", axis=1
    ).tolist()
    
    col_sel, col_btn = st.columns([4, 1])
    with col_sel:
        socio_sel = st.selectbox("Seleccionar para gestionar:", opciones_socios, label_visibility="collapsed")
    with col_btn:
        if st.button("🔧 Modificar / Eliminar"):
            st.session_state.mostrar_editor = True
            st.session_state.id_socio_a_editar = int(socio_sel.split(" - ")[0])
            st.rerun()

else:
    st.info("No hay socios registrados.")

# ==========================================
# 3. PANEL DE EDICIÓN
# ==========================================
if st.session_state.mostrar_editor and st.session_state.id_socio_a_editar is not None:
    st.write("---")
    
    if st.session_state.id_socio_a_editar == 0:
        socios_filtrados = df_socios[df_socios['idsocio'].isna()]
    else:
        socios_filtrados = df_socios[df_socios['idsocio'] == st.session_state.id_socio_a_editar]
    
    if not socios_filtrados.empty:
        s = socios_filtrados.iloc[0]
        id_actual = int(s['idsocio']) if pd.notna(s['idsocio']) else 0
        st.info(f"⚙️ Editando a: {s['nombre']} {s['apellido']} (ID: {id_actual})")
        
        col_e, col_d = st.columns([2, 1])
        with col_e:
            with st.container(border=True):
                st.write("✏️ **Editar Datos**")
                es_activo = True if str(s['activo']).strip() in ['1', '1.0'] else False
                nuevo_estado = st.checkbox("🟢 Socio Activo", value=es_activo)
                
                n = st.text_input("Nombre", value=str(s['nombre']))
                a = st.text_input("Apellido", value=str(s['apellido']))
                d = st.text_input("DNI", value=str(s['dni']) if pd.notna(s['dni']) else "")
                
                nombre_plan_actual = s.get('nombreplan', '')
                index_plan = lista_planes.index(nombre_plan_actual) if nombre_plan_actual in lista_planes else 0
                nuevo_plan = st.selectbox("Plan", lista_planes, index=index_plan, key="edit_plan")
                
                try:
                    venc_actual = datetime.strptime(str(s['fechavencimiento']), '%Y-%m-%d').date()
                except:
                    venc_actual = datetime.today().date()
                    
                nuevo_venc = st.date_input("Vencimiento", value=venc_actual)
                sald = st.number_input("Saldo Actual ($)", value=float(s['saldo']) if pd.notna(s['saldo']) else 0.0)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("Actualizar"):
                        estado_bit = 1 if nuevo_estado else 0
                        nuevo_id_plan = None
                        if not df_planes.empty and nuevo_plan != "Sin planes":
                            nuevo_id_plan = int(df_planes[df_planes['nombreplan'] == nuevo_plan]['idplan'].iloc[0])
                        
                        if id_actual == 0:
                            res = ejecutar_query(
                                "UPDATE Socios SET Nombre=?, Apellido=?, IdPlan=?, FechaVencimiento=?, Saldo=?, Activo=? WHERE DNI=?",
                                [n, a, nuevo_id_plan, nuevo_venc.strftime('%Y-%m-%d'), float(sald), estado_bit, d]
                            )
                        else:
                            res = ejecutar_query(
                                "UPDATE Socios SET Nombre=?, Apellido=?, DNI=?, IdPlan=?, FechaVencimiento=?, Saldo=?, Activo=? WHERE IdSocio=?",
                                [n, a, d, nuevo_id_plan, nuevo_venc.strftime('%Y-%m-%d'), float(sald), estado_bit, id_actual]
                            )
                        
                        str_res = str(res).lower()
                        if "error" in str_res or ("message" in res and "results" not in res):
                            st.error("⚠️ No se pudo actualizar.")
                        else:
                            st.session_state.mostrar_editor = False
                            st.rerun()
                            
                with col_btn2:
                    if st.button("❌ Cancelar / Cerrar Editor"):
                        st.session_state.mostrar_editor = False
                        st.rerun()
        
        with col_d:
            with st.container(border=True):
                st.write("🗑️ **Eliminar Socio**")
                
                # --- DOBLE CHECK PARA BORRAR SOCIO ---
                with st.popover("🗑️ Eliminar"):
                    st.warning(f"🚨 Se eliminará a {s['nombre']} {s['apellido']} y TODO su historial de pagos permanentemente.")
                    if st.button("Sí, Eliminar todo", type="primary"):
                        if id_actual == 0:
                            # 1. Borramos pagos buscando por un subquery con el DNI
                            ejecutar_query("DELETE FROM Pagos WHERE IdSocio IN (SELECT IdSocio FROM Socios WHERE DNI=?)", [str(s['dni'])])
                            # 2. Borramos al socio
                            res = ejecutar_query("DELETE FROM Socios WHERE DNI=?", [str(s['dni'])])
                        else:
                            # 1. Borrado en cascada: Eliminamos primero los pagos para que no queden huerfanos
                            ejecutar_query("DELETE FROM Pagos WHERE IdSocio=?", [id_actual])
                            # 2. Borramos al socio
                            res = ejecutar_query("DELETE FROM Socios WHERE IdSocio=?", [id_actual])
                        
                        st.session_state.mostrar_editor = False
                        st.rerun()
    else:
        st.error("Socio no encontrado. Por favor, recargá la página.")
        st.session_state.mostrar_editor = False
