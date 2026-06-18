import streamlit as st
import pandas as pd
import requests
from database.conexion import get_connection

st.set_page_config(page_title="Panel de Administración", layout="wide")
st.title("Sistema Administrativo")

# --- CONEXIÓN A TURSO ---
url, token = get_connection()

def ejecutar_query(query, params=()):
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
        clean_rows = [[cell['value'] if isinstance(cell, dict) and 'value' in cell else cell for cell in row] for row in rows]
        return pd.DataFrame(clean_rows, columns=cols)
    except:
        return pd.DataFrame()

# --- CREACIÓN DE TABLAS EN LA NUBE ---
# Ahora tus rutinas y ejercicios también viven en Turso
ejecutar_query("CREATE TABLE IF NOT EXISTS Ejercicios (IdEjercicio INTEGER PRIMARY KEY AUTOINCREMENT, Nombre TEXT UNIQUE)")
ejecutar_query("""CREATE TABLE IF NOT EXISTS Rutina_General (
        IdRutinaGen INTEGER PRIMARY KEY AUTOINCREMENT,
        DiaSemana TEXT,
        Bloque TEXT,
        IdEjercicio INTEGER,
        Repeticiones TEXT,
        Detalle TEXT,
        VideoUrl TEXT,
        TecnicaNota TEXT
    )""")

st.success("✅ Conexión a la nube verificada. Sistema en línea.")
st.divider()

# --- BOTONES DE RESPALDO DE DATOS ---
st.subheader("⚙️ Mantenimiento y Respaldo")
st.write("Tu base de datos está segura en la nube. Podés descargar copias de seguridad de tus registros en formato Excel desde aquí:")

# Leemos todas las tablas principales
df_soc = leer_tabla("SELECT * FROM Socios")
df_pag = leer_tabla("SELECT * FROM Pagos")
df_pla = leer_tabla("SELECT * FROM Planes")

col1, col2, col3 = st.columns(3)

with col1:
    if not df_soc.empty:
        csv_soc = df_soc.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
        st.download_button(label="💾 Backup Socios", data=csv_soc, file_name="backup_socios.csv", mime="text/csv", type="primary")
    else:
        st.button("💾 Backup Socios (Vacío)", disabled=True)

with col2:
    if not df_pag.empty:
        csv_pag = df_pag.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
        st.download_button(label="💾 Backup Pagos", data=csv_pag, file_name="backup_pagos.csv", mime="text/csv", type="primary")
    else:
        st.button("💾 Backup Pagos (Vacío)", disabled=True)

with col3:
    if not df_pla.empty:
        csv_pla = df_pla.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
        st.download_button(label="💾 Backup Planes", data=csv_pla, file_name="backup_planes.csv", mime="text/csv", type="primary")
    else:
        st.button("💾 Backup Planes (Vacío)", disabled=True)
