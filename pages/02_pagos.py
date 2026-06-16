import streamlit as st
import pandas as pd
from datetime import datetime
from database.conexion import get_connection

st.set_page_config(page_title="Caja y Pagos", layout="wide")
st.title("💸 Ingreso de Pagos")
conn = get_connection()

# Traemos socios activos
df_socios = pd.read_sql("SELECT IdSocio, Nombre, Apellido, DNI, Saldo FROM Socios WHERE Activo = 1", conn)

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
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Pagos (IdSocio, Monto, MetodoPago, FechaPago) VALUES (?,?,?,?)", (id_socio, monto, metodo, datetime.today().date()))
            cursor.execute("UPDATE Socios SET Saldo=Saldo+? WHERE IdSocio=?", (monto, id_socio))
            conn.commit()
            st.rerun()

st.divider()
st.subheader("📋 Historial de Pagos")
df_historial = pd.read_sql("SELECT P.*, S.Nombre, S.Apellido FROM Pagos P JOIN Socios S ON P.IdSocio = S.IdSocio ORDER BY P.FechaPago DESC", conn)

if not df_historial.empty:
    # Mostramos historial con opción a borrar
    for i, row in df_historial.iterrows():
        c1, c2 = st.columns([3, 1])
        c1.write(f"{row['FechaPago']} | {row['Nombre']} {row['Apellido']} | ${row['Monto']:,.2f} | {row['MetodoPago']}")
        if c2.button("🗑️", key=f"del_{row['IdPago']}"):
            conn.cursor().execute("UPDATE Socios SET Saldo=Saldo-? WHERE IdSocio=?", (row['Monto'], row['IdSocio']))
            conn.cursor().execute("DELETE FROM Pagos WHERE IdPago=?", (row['IdPago'],))
            conn.commit()
            st.rerun()
