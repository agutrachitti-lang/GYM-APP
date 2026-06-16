import streamlit as st
import pandas as pd
from datetime import datetime
from database.conexion import get_connection

st.set_page_config(page_title="Caja y Pagos", layout="wide")

# CSS para botón verde
st.markdown("""<style>button[kind="primary"] { background-color: #28a745 !important; color: white !important; }</style>""", unsafe_allow_html=True)

st.title("💸 Ingreso de Pagos")
conn = get_connection()

# --- CARGA SEGURA DE SOCIOS ---
try:
    df_socios = pd.read_sql("SELECT IdSocio, Nombre, Apellido, DNI, Saldo FROM Socios WHERE Activo = 1", conn)
except:
    df_socios = pd.DataFrame()

if df_socios.empty:
    st.warning("No hay socios activos registrados.")
else:
    with st.container(border=True):
        st.subheader("💵 Registrar Pago")
        opciones_socios = df_socios.apply(lambda row: f"{row['IdSocio']} - DNI: {row['DNI']} - {row['Nombre']} {row['Apellido']}", axis=1).tolist()
        socio_sel = st.selectbox("1. Seleccionar Socio", opciones_socios)
        id_socio = int(socio_sel.split(" - ")[0])
        metodo_pago = st.selectbox("2. Método", ["Efectivo", "Transferencia", "MercadoPago", "Tarjeta"])
        
        datos_socio = df_socios[df_socios['IdSocio'] == id_socio].iloc[0]
        saldo_actual = float(datos_socio['Saldo'])
        st.write(f"**3. Saldo actual:** ${saldo_actual:,.2f}")
        monto_pagado = st.number_input("4. Monto a ingresar ($)", min_value=0.0, step=1000.0)

        if st.button("✅ Confirmar Pago", use_container_width=True, type="primary"):
            if monto_pagado > 0:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Pagos (IdSocio, Monto, MetodoPago, FechaPago) VALUES (?, ?, ?, ?)",
                               (id_socio, float(monto_pagado), metodo_pago, datetime.today().date()))
                cursor.execute("UPDATE Socios SET Saldo = Saldo + ? WHERE IdSocio=?", (float(monto_pagado), id_socio))
                conn.commit()
                st.success("¡Pago registrado!")
                st.rerun()

st.divider()
st.subheader("📋 Gestión de Pagos")

# --- CARGA SEGURA DE HISTORIAL ---
try:
    query_historial = "SELECT P.IdPago, P.IdSocio, S.Nombre, S.Apellido, P.Monto, P.MetodoPago, P.FechaPago FROM Pagos P INNER JOIN Socios S ON P.IdSocio = S.IdSocio ORDER BY P.FechaPago DESC"
    df_historial = pd.read_sql(query_historial, conn)
except:
    df_historial = pd.DataFrame()

if not df_historial.empty:
    opciones = df_historial.apply(lambda row: f"{row['IdPago']} - {row['Nombre']} {row['Apellido']} | ${row['Monto']:.2f} | {row['FechaPago']}", axis=1).tolist()
    pago_sel = st.selectbox("Seleccionar pago para eliminar:", opciones)
    id_pago = int(pago_sel.split(" - ")[0])
    
    # Buscamos el pago en el DataFrame ya cargado (sin consultar de nuevo la DB borrada)
    pago_data = df_historial[df_historial['IdPago'] == id_pago].iloc[0]
    
    if st.expander("🗑️ Eliminar este pago"):
        if st.button("Sí, borrar pago y revertir saldo"):
            cursor = conn.cursor()
            # 1. Revertir saldo ANTES de borrar el pago (usamos el IdSocio que ya tenemos en pago_data)
            cursor.execute("UPDATE Socios SET Saldo = Saldo - ? WHERE IdSocio=?", (float(pago_data['Monto']), int(pago_data['IdSocio'])))
            # 2. Borrar el pago
            cursor.execute("DELETE FROM Pagos WHERE IdPago=?", (id_pago,))
            conn.commit()
            st.success("Pago eliminado.")
            st.rerun()
