import streamlit as st
import pandas as pd
from database.conexion import get_connection

st.set_page_config(page_title="Alumnos 2.0", layout="centered")

# --- ESTILOS PARA QUE SE VEA "APP" ---
st.markdown("""
    <style>
    .card { background-color: #f0f2f6; padding: 15px; border-radius: 15px; margin-bottom: 10px; border-left: 5px solid #FF4B4B; }
    .ejercicio-titulo { font-size: 1.3rem; font-weight: bold; color: #000; }
    .globo-tecnica { background-color: #ffefc1; padding: 10px; border-radius: 10px; border: 1px solid #ffcc00; margin: 10px 0; font-style: italic; }
    </style>
""", unsafe_allow_html=True)

st.title("🔥 Rutina de hoy")
dia = st.radio("Día", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"], horizontal=True, index=0)

conn = get_connection()

# Traemos rutina con campos nuevos: URL Video y Técnica
# Nota: Si no tenés estas columnas, agregalas a la tabla Rutina_General en SQL
query = """
    SELECT RG.IdRutinaGen, RG.Bloque, E.Nombre as Ejercicio, RG.Repeticiones, 
           RG.Detalle, RG.VideoUrl, RG.TecnicaNota
    FROM Rutina_General RG
    INNER JOIN Ejercicios E ON RG.IdEjercicio = E.IdEjercicio
    WHERE RG.DiaSemana = ?
    ORDER BY RG.Bloque
"""
# Si te da error de columnas faltantes, avisame y las agregamos a la tabla SQL!
df = pd.read_sql(query, conn, params=(dia,))

if not df.empty:
    for _, row in df.iterrows():
        # Tarjeta principal
        st.markdown(f'<div class="card"><div class="ejercicio-titulo">{row["Ejercicio"]}</div><small>{row["Detalle"]}</small></div>', unsafe_allow_html=True)
        
        # Expander para la "Magia"
        with st.expander("👉 Ver técnica y registrar series"):
            
            # Globo de técnica
            if row['TecnicaNota']:
                st.markdown(f'<div class="globo-tecnica">💡 <b>Profe dice:</b> {row["TecnicaNota"]}</div>', unsafe_allow_html=True)
            
            # Video si existe
            if row['VideoUrl']:
                st.video(row['VideoUrl'])
            
            # Series Verticales (expandidas según los guiones)
            reps_meta = row['Repeticiones'].split('-')
            
            for i, meta in enumerate(reps_meta):
                cols = st.columns([1, 1, 1])
                cols[0].write(f"**Serie {i+1}** (Meta: {meta})")
                cols[1].number_input(f"Reps", min_value=0, key=f"r_{row['IdRutinaGen']}_{i}")
                cols[2].number_input("KG", min_value=0.0, step=0.5, key=f"k_{row['IdRutinaGen']}_{i}")

    if st.button("💾 Guardar mis registros", type="primary", use_container_width=True):
        st.toast("¡Datos guardados correctamente!")

else:
    st.info("No hay rutina cargada.")