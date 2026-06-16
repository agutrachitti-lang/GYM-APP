import streamlit as st
import pandas as pd
from database.conexion import get_connection

st.set_page_config(page_title="Pizarra de Entrenamiento", layout="wide")
st.title("🏋️‍♂️ Pizarra de Entrenamiento")

conn = get_connection()
dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
bloques_entrenamiento = ["E.C."] + [f"B{i}" for i in range(1, 21)] + ["Finisher"]

tab_general, tab_excepcion, tab_ejercicios = st.tabs(["📅 Pizarra General", "👤 Excepciones", "📚 Catálogo"])

# --- FUNCION DE ORDENAMIENTO (para evitar SQL Server functions) ---
def ordenar_bloques(df):
    orden = {b: i for i, b in enumerate(bloques_entrenamiento)}
    df['Orden'] = df['Bloque'].map(orden).fillna(99)
    return df.sort_values(['Orden', 'IdRutinaGen'])

# ==========================================
# PESTAÑA 3: CATÁLOGO
# ==========================================
with tab_ejercicios:
    col_ej1, col_ej2 = st.columns([1, 2])
    with col_ej1:
        with st.form("form_ej", clear_on_submit=True):
            nombre_ej = st.text_input("Nombre del Ejercicio")
            if st.form_submit_button("Guardar"):
                if nombre_ej:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Ejercicios (Nombre) VALUES (?)", (nombre_ej.strip().title(),))
                    conn.commit()
                    st.rerun()
    with col_ej2:
        df_ej = pd.read_sql("SELECT * FROM Ejercicios ORDER BY Nombre", conn)
        st.dataframe(df_ej, use_container_width=True)

# ==========================================
# PESTAÑA 1: PIZARRA GENERAL
# ==========================================
with tab_general:
    df_ej = pd.read_sql("SELECT * FROM Ejercicios", conn)
    if df_ej.empty:
        st.warning("Cargá ejercicios primero.")
    else:
        dia_sel = st.selectbox("Seleccionar Día:", dias_semana)
        col_form, col_lista = st.columns([1, 2])
        
        with col_form:
            bloque_sel = st.selectbox("Bloque", bloques_entrenamiento)
            ej_sel = st.selectbox("Ejercicio", df_ej.apply(lambda r: f"{r['IdEjercicio']} - {r['Nombre']}", axis=1))
            cant_series = st.number_input("Series", 1, 10, 3)
            reps = [st.text_input(f"S{i+1}", key=f"s{i}") for i in range(cant_series)]
            detalle = st.text_input("Aclaración")
            
            if st.button("➕ Agregar"):
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Rutina_General (DiaSemana, Bloque, IdEjercicio, Repeticiones, Detalle) VALUES (?,?,?,?,?)",
                               (dia_sel, bloque_sel, int(ej_sel.split(" - ")[0]), "-".join([r for r in reps if r]), detalle))
                conn.commit()
                st.rerun()

        with col_lista:
            df_gen = pd.read_sql("SELECT RG.*, E.Nombre as Ejercicio FROM Rutina_General RG JOIN Ejercicios E ON RG.IdEjercicio=E.IdEjercicio WHERE DiaSemana=?", conn, params=(dia_sel,))
            if not df_gen.empty:
                df_gen = ordenar_bloques(df_gen)
                st.dataframe(df_gen[['Bloque', 'Ejercicio', 'Repeticiones', 'Detalle']], hide_index=True)

# ==========================================
# PESTAÑA 2: EXCEPCIONES
# ==========================================
with tab_excepcion:
    df_socios = pd.read_sql("SELECT IdSocio, Nombre, Apellido FROM Socios WHERE Activo=1", conn)
    if not df_socios.empty:
        socio_sel = st.selectbox("Alumno", df_socios.apply(lambda r: f"{r['IdSocio']} - {r['Nombre']} {r['Apellido']}", axis=1))
        # ... lógica similar a la de arriba ...
