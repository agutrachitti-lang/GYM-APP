import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from database.conexion import get_connection

st.set_page_config(page_title="Caja y Pagos", layout="wide")
st.title("💸 Ingreso de Pagos")

# --- ADAPTACIÓN API TURSO ---
url, token = get_connection()

def ejecutar_query(query, params=()):
    payload = {"statements": [{"q": query, "params": params}]}
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{url}/v2/pipeline", json=payload, headers=headers)
    return response.json()

def leer_tabla(query):
    res = ejecutar_query(query)
    try:
        data = res['results'][0]['response']['result']
        return pd.DataFrame(data['rows'], columns=[c['name'] for c in data['cols']])
    except:
        return pd.DataFrame()

# --- TRAEMOS SOCIOS ACTIVOS ---
df_socios = leer_tabla("SELECT IdSocio, Nombre, Apellido, DNI FROM Socios WHERE Activo = 1")

if df_socios.empty:
    st.warning("No hay socios activos registrados.")
else:
    with st.container(border=True):
        st.subheader("💵 Registrar Pago")
        opciones_socios = df_socios.apply(lambda r: f"{r['IdSocio']} - DNI: {r['DNI']} - {r['Nombre']} {r['Apellido']}", axis=1).tolist()
        socio_sel = st.selectbox("1. Seleccionar Socio", opciones_socios)
        metodo = st.selectbox("2. Método de Pago", ["Efectivo", "Transferencia", "MercadoPago", "Tarjeta"])
        monto = st.number_input("3. Monto ($)", min_value=0.0, step=1000.0)

        if st.button("✅ Confirmar Pago", type="primary"):
            id_socio = int(socio_sel.split(" - ")[0])
            fecha_hoy = datetime.today().strftime('%Y-%m-%d')
            
            # Insertar Pago
            ejecutar_query("INSERT INTO Pagos (IdSocio, Monto, MetodoPago, FechaPago) VALUES (?,?,?,?)", [id_socio, monto, metodo, fecha_hoy])
            # Actualizar Saldo
            ejecutar_query("UPDATE Socios SET Saldo = Saldo + ? WHERE IdSocio = ?", [monto, id_socio])
            
            st.success("Pago registrado correctamente.")
            st.rerun()

st.divider()
st.subheader("📋 Historial de Pagos")
df_historial = leer_tabla("SELECT P.*, S.Nombre, S.Apellido FROM Pagos P JOIN Socios S ON P.IdSocio = S.IdSocio ORDER BY P.FechaPago DESC")

if not df_historial.empty:
    for i, row in df_historial.iterrows():
        c1, c2 = st.columns([3, 1])
        c1.write(f"{row['FechaPago']} | {row['Nombre']} {row['Apellido']} | ${float(row['Monto']):,.2f} | {row['MetodoPago']}")
        if c2.button("🗑️", key=f"del_{row['IdPago']}"):
            # Revertir Saldo y Borrar Pago
            ejecutar_query("UPDATE Socios SET Saldo = Saldo - ? WHERE IdSocio = ?", [row['Monto'], row['IdSocio']])
            ejecutar_query("DELETE FROM Pagos WHERE IdPago = ?", [row['IdPago']])
            st.rerun()
