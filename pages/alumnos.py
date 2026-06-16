import streamlit as st
import pandas as pd
from database.conexion import get_connection

st.set_page_config(page_title="Pizarra de Entrenamiento", layout="centered")

# CSS para tarjetas tipo APP con COLORES CORREGIDOS para legibilidad
st.markdown("""
    <style>
    .card { background-color: #ffffff; padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 10px; border-left: 5px solid #FF4B4B; }
    .bloque-header { font-size: 1.4rem; font-weight: 800; color: #333333; margin: 25px 0 10px 0; padding-bottom: 5px; border-bottom: 1px solid #ddd; }
    .ejercicio-nombre { font-size: 1.2rem; font-weight: bold; margin-bottom: 5px; color: #000000; } /* COLOR NEGRO PARA EL NOMBRE */
    .ejercicio-detalle { font-size: 0.9rem; color: #555555; } /* COLOR GRIS OSCURO PARA EL DETALLE */
    </style>
""", unsafe_allow_html=True)

st.title("🔥 Pizarra del Día")

conn = get_connection()
dia = st.radio("Día", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"], horizontal=True)

# Consulta SQL ordenada por Bloque (E.C. primero, luego B1, B2...)
query = """
    SELECT RG.Bloque, E.Nombre as Ejercicio, RG.Repeticiones, RG.Detalle 
    FROM Rutina_General RG
    INNER JOIN Ejercicios E ON RG.IdEjercicio = E.IdEjercicio
    WHERE RG.DiaSemana = ?
    ORDER BY 
        CASE WHEN RG.Bloque = 'E.C.' THEN 0 
             WHEN RG.Bloque = 'Finisher' THEN 99 
             ELSE CAST(SUBSTRING(RG.Bloque, 2, LEN(RG.Bloque)) AS INT) 
        END ASC, RG.IdRutinaGen ASC
"""
df = pd.read_sql(query, conn, params=(dia,))

if not df.empty:
    # Agrupamos por bloque único para no repetir el título
    bloques = df['Bloque'].unique()
    
    for b in bloques:
        # Título del bloque (E.C., B1, B2, etc.)
        st.markdown(f'<p class="bloque-header">{b}</p>', unsafe_allow_html=True)
        
        # Filtramos solo los ejercicios de este bloque
        df_bloque = df[df['Bloque'] == b]
        
        for _, row in df_bloque.iterrows():
            # Tarjeta de ejercicio con COLORES CORREGIDOS
            st.markdown(f"""
                <div class="card">
                    <div class="ejercicio-nombre">{row['Ejercicio']}</div>
                    <div class="ejercicio-detalle">{row['Detalle']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Series dinámicas para anotar
            series = row['Repeticiones'].split('-')
            
            # Usamos un expander por ejercicio para que sea "retraíble"
            with st.expander("📝 Anotar mis series"):
                for i, meta in enumerate(series):
                    cols = st.columns(3)
                    cols[0].markdown(f"**Serie {i+1}** <br> <small>Meta: {meta}</small>", unsafe_allow_html=True)
                    cols[1].number_input(f"Reps", min_value=0, key=f"r_{row['Ejercicio']}_{i}")
                    cols[2].number_input("KG", min_value=0.0, step=0.5, key=f"k_{row['Ejercicio']}_{i}")
            
    st.write("")
    st.button("💾 Guardar registros del día", type="primary", use_container_width=True)
else:
    st.info("No hay rutina cargada para este día.")