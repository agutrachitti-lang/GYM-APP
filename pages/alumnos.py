import streamlit as st
import pandas as pd
from database.conexion import get_connection

st.set_page_config(page_title="Pizarra de Entrenamiento", layout="centered")

st.markdown("""
    <style>
    .card { background-color: #ffffff; padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 10px; border-left: 5px solid #FF4B4B; }
    .bloque-header { font-size: 1.4rem; font-weight: 800; color: #333333; margin: 25px 0 10px 0; padding-bottom: 5px; border-bottom: 1px solid #ddd; }
    .ejercicio-nombre { font-size: 1.2rem; font-weight: bold; margin-bottom: 5px; color: #000000; }
    .ejercicio-detalle { font-size: 0.9rem; color: #555555; }
    </style>
""", unsafe_allow_html=True)

st.title("🔥 Pizarra del Día")

conn = get_connection()
dia = st.radio("Día", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"], horizontal=True)

# CONSULTA CORREGIDA PARA SQLITE
# Eliminamos funciones de SQL Server que rompían la App
query = """
    SELECT RG.Bloque, E.Nombre as Ejercicio, RG.Repeticiones, RG.Detalle 
    FROM Rutina_General RG
    INNER JOIN Ejercicios E ON RG.IdEjercicio = E.IdEjercicio
    WHERE RG.DiaSemana = ?
    ORDER BY RG.Bloque ASC, RG.IdRutinaGen ASC
"""

try:
    df = pd.read_sql(query, conn, params=(dia,))
except Exception as e:
    st.error(f"Error al leer la base de datos: {e}")
    df = pd.DataFrame()

if not df.empty:
    bloques = df['Bloque'].unique()
    
    for b in bloques:
        st.markdown(f'<p class="bloque-header">{b}</p>', unsafe_allow_html=True)
        df_bloque = df[df['Bloque'] == b]
        
        for _, row in df_bloque.iterrows():
            st.markdown(f"""
                <div class="card">
                    <div class="ejercicio-nombre">{row['Ejercicio']}</div>
                    <div class="ejercicio-detalle">{row['Detalle']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            series = str(row['Repeticiones']).split('-')
            
            with st.expander("📝 Anotar mis series"):
                for i, meta in enumerate(series):
                    cols = st.columns(3)
                    cols[0].markdown(f"**Serie {i+1}** <br> <small>Meta: {meta}</small>", unsafe_allow_html=True)
                    cols[1].number_input(f"Reps", min_value=0, key=f"r_{row['Ejercicio']}_{i}")
                    cols[2].number_input("KG", min_value=0.0, step=0.5, key=f"k_{row['Ejercicio']}_{i}")
            
    st.button("💾 Guardar registros del día", type="primary", use_container_width=True)
else:
    st.info("No hay rutina cargada para este día.")
