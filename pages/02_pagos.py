import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from database.conexion import get_connection

st.set_page_config(page_title="Caja y Pagos", layout="wide")
st.title("💸 Ingreso de Pagos")

# --- CONEXIÓN A TURSO ---
url, token = get_connection()

def ejecutar_query(query, params=()):
    # Usamos la misma estructura blindada que en socios.py
    formatted_params = []
    for p in params:
        if p is None: formatted_params.append({"type": "null"})
        elif isinstance(p, int): formatted_params.append({"type": "integer", "value": str(p)})
        elif isinstance(p, float): formatted_params.append({"type": "float", "value": float(p)})
        else: formatted_params.append({"type": "text", "value": str(p)})

    payload = {"requests": [{"type": "execute", "stmt": {"sql": query, "args": formatted_params}}]}
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
        # Limpiamos tipos de datos
        for col in ['idsocio', 'idpago', 'monto', 'saldo']:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except:
        return pd.DataFrame()

# --- CARGAR DATOS ---
df_socios = leer_tabla("SELECT idsocio, nombre, apellido, dni, saldo FROM Socios WHERE activo = 1")
df_historial = leer_tabla("SELECT P.*, S.nombre, S.apellido FROM Pagos P JOIN Socios S ON P.idsocio = S.idsocio ORDER BY P.fechapago DESC")

# --- PANEL DE PAGO ---
with st.container(border=True):
    st.subheader("💵 Registrar Pago")
    if df_socios.empty:
        st.warning("No hay socios activos registrados.")
    else:
        opciones_socios = df_socios.apply(lambda r: f"{int(r['idsocio'])} - DNI: {r['dni']} - {r['nombre']} {r['apellido']}", axis=1).tolist()
        socio_sel = st.selectbox("1. Seleccionar Socio Activo", opciones_socios)
        
        # Obtener saldo actual
        id_socio_sel = int(socio_sel.split(" - ")[0])
        saldo_actual = df_socios[df_socios['idsocio'] == id_socio_sel]['saldo'].iloc[0]
        
        st.info(f"💰 SALDO: ${float(saldo_actual):,.2f}")
        
        metodo = st.selectbox("2. Método de Pago", ["Efectivo", "Transferencia", "MercadoPago", "Tarjeta"])
        monto = st.number_input("3. Monto a ingresar ($)", min_value=0.0, step=1000.0)

        if st.button("✅ Confirmar Pago", type="primary"):
            fecha_hoy = datetime.today().strftime('%Y-%m-%d')
            # 1. Insertar Pago
            ejecutar_query("INSERT INTO Pagos (IdSocio, Monto, MetodoPago, FechaPago) VALUES (?,?,?,?)", 
                           [id_socio_sel, float(monto), metodo, fecha_hoy])
            # 2. Actualizar Saldo
            ejecutar_query("UPDATE Socios SET Saldo = Saldo + ? WHERE IdSocio = ?", 
                           [float(monto), id_socio_sel])
            
            st.success("Pago registrado correctamente.")
            st.rerun()

st.divider()
st.subheader("📋 Gestión de Pagos Realizados")

if not df_historial.empty:
    st.write("### Últimos Ingresos")
    for i, row in df_historial.iterrows():
        c1, c2 = st.columns([3, 1])
        c1.write(f"{row['fechapago']} | **{row['nombre']} {row['apellido']}** | ${float(row['monto']):,.2f} | {row['metodopago']}")
        
        # --- DOBLE CHECK PARA ELIMINAR ---
        with c2:
            # Usamos un expander para que el usuario tenga que interactuar dos veces
            with st.popover("🗑️ Eliminar"):
                st.warning(f"¿Seguro que querés borrar este pago de ${float(row['monto']):,.2f} de {row['nombre']}?")
                if st.button("Sí, borrar definitivamente", key=f"del_{row['idpago']}", type="primary"):
                    # Revertir Saldo y Borrar Pago
                    ejecutar_query("UPDATE Socios SET Saldo = Saldo - ? WHERE IdSocio = ?", [float(row['monto']), int(row['idsocio'])])
                    ejecutar_query("DELETE FROM Pagos WHERE IdPago = ?", [int(row['idpago'])])
                    st.rerun()
else:
    st.info("No hay pagos registrados.")
