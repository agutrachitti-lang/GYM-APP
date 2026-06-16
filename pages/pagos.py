import streamlit as st
import pandas as pd
from datetime import datetime
from database.conexion import get_connection

st.set_page_config(page_title="Caja y Pagos", layout="wide")

# --- INYECCIÓN DE CSS PARA EL BOTÓN VERDE ---
st.markdown("""
    <style>
    button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border-color: #28a745 !important;
    }
    button[kind="primary"]:hover {
        background-color: #218838 !important;
        border-color: #1e7e34 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💸 Ingreso de Pagos")

conn = get_connection()

# Traemos a los socios ACTIVOS y ahora también incluimos el DNI
df_socios = pd.read_sql("SELECT IdSocio, Nombre, Apellido, DNI, Saldo FROM Socios WHERE Activo = 1", conn)

if df_socios.empty:
    st.warning("No hay socios activos registrados para cobrarles.")
else:
    # --- NUEVO DISEÑO: Todo en un solo cuadro ---
    with st.container(border=True):
        st.subheader("💵 Registrar Pago")

        # 1. Elegir socio (Ahora muestra el DNI para buscar más fácil)
        opciones_socios = df_socios.apply(
            lambda row: f"{row['IdSocio']} - DNI: {row['DNI']} - {row['Nombre']} {row['Apellido']}", axis=1
        ).tolist()
        socio_sel = st.selectbox("1. Seleccionar Socio Activo", opciones_socios)
        id_socio = int(socio_sel.split(" - ")[0])

        # 2. Método de Pago
        metodo_pago = st.selectbox("2. Método de Pago", ["Efectivo", "Transferencia", "MercadoPago", "Tarjeta"])

        # 3. Estado de cuenta (Saldo dinámico)
        datos_socio = df_socios[df_socios['IdSocio'] == id_socio].iloc[0]
        saldo_actual = float(datos_socio['Saldo'])

        st.write("**3. Saldo en cuenta:**")
        if saldo_actual < 0:
            st.error(f"💰 DEBE: **${abs(saldo_actual):,.2f}**")
        elif saldo_actual > 0:
            st.success(f"💰 A FAVOR: **${saldo_actual:,.2f}**")
        else:
            st.info(f"💰 AL DÍA: **$0.00**")

        # 4. Monto a ingresar
        monto_pagado = st.number_input("4. Monto a ingresar ($)", min_value=0.0, step=1000.0)

        st.write("") # Espacio visual
        
        # 5. Botón (Toma el color verde gracias al CSS de arriba)
        btn_pago = st.button("✅ Confirmar Pago", use_container_width=True, type="primary")

        if btn_pago:
            if monto_pagado > 0:
                nuevo_saldo = saldo_actual + monto_pagado
                cursor = conn.cursor()
                
                # 1. Guardar recibo
                cursor.execute("INSERT INTO Pagos (IdSocio, Monto, MetodoPago, FechaPago) VALUES (?, ?, ?, ?)",
                               (id_socio, float(monto_pagado), metodo_pago, datetime.today().date()))
                # 2. Sumar al saldo
                cursor.execute("UPDATE Socios SET Saldo=? WHERE IdSocio=?", (float(nuevo_saldo), id_socio))
                
                conn.commit()
                st.success(f"¡Pago de ${monto_pagado:,.2f} registrado! El saldo se actualizó.")
                st.rerun()
            else:
                st.error("El monto debe ser mayor a 0.")

st.divider()

# ==========================================
# GESTIÓN DE PAGOS Y CUBIERTA DE ERRORES
# ==========================================
st.subheader("📋 Gestión de Pagos Realizados")

query_historial = """
    SELECT P.IdPago, S.Nombre, S.Apellido, P.Monto, P.MetodoPago, P.FechaPago 
    FROM Pagos P 
    INNER JOIN Socios S ON P.IdSocio = S.IdSocio 
    ORDER BY P.FechaPago DESC, P.IdPago DESC
"""
df_historial = pd.read_sql(query_historial, conn)

if not df_historial.empty:
    def formatear_opcion(row):
        fecha = pd.to_datetime(row['FechaPago']).strftime('%d/%m/%Y')
        monto_fmt = f"${float(row['Monto']):,.2f}"
        return f"{row['IdPago']} - {row['Nombre']} {row['Apellido']} | {monto_fmt} | {fecha} | {row['MetodoPago']}"

    opciones = df_historial.apply(formatear_opcion, axis=1).tolist()
    mapa_pagos = {opcion: df_historial.iloc[i]['IdPago'] for i, opcion in enumerate(opciones)}
    
    pago_seleccionado = st.selectbox("Seleccionar pago para eliminar:", opciones)
    id_pago = mapa_pagos[pago_seleccionado]
    
    pago_data = df_historial[df_historial['IdPago'] == id_pago].iloc[0]
    
    # Dejamos solo 2 columnas: Info y Botón de Borrar
    col_info, col_btn_d = st.columns([2, 1])
    
    with col_info:
        st.write(f"**Detalle del recibo:** {pago_data['Nombre']} {pago_data['Apellido']} - ${float(pago_data['Monto']):,.2f} - {pago_data['MetodoPago']}")
            
    with col_btn_d:
        # Usamos un expander como medida de seguridad antes del botón
        with st.expander("🗑️ Eliminar este pago"):
            st.warning(f"¿Seguro que querés borrar el pago de **${float(pago_data['Monto']):,.2f}** de **{pago_data['Nombre']} {pago_data['Apellido']}**?")
            
            if st.button("Sí, borrar pago y revertir saldo"):
                monto_borrar = float(pago_data['Monto'])
                id_pago_limpio = int(id_pago)
                
                cursor = conn.cursor()
                
                # Borrar el pago
                cursor.execute("DELETE FROM Pagos WHERE IdPago=?", (id_pago_limpio,))
                # Revertir el saldo
                cursor.execute("UPDATE Socios SET Saldo = Saldo - ? WHERE IdSocio IN (SELECT IdSocio FROM Pagos WHERE IdPago=?)", (monto_borrar, id_pago_limpio))
                
                conn.commit()
                st.success("Pago eliminado y saldo actualizado.")
                st.rerun()

st.divider()

# ==========================================
# HISTORIAL GENERAL DE CAJA
# ==========================================
st.subheader("Últimos Ingresos")
if not df_historial.empty:
    df_mostrar = df_historial.copy()
    df_mostrar['Monto'] = df_mostrar['Monto'].map('${:,.2f}'.format)
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)