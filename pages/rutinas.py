import streamlit as st
import pandas as pd
from database.conexion import get_connection

st.set_page_config(page_title="Pizarra de Entrenamiento", layout="wide")
st.title("🏋️‍♂️ Pizarra de Entrenamiento")

conn = get_connection()
dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
bloques_entrenamiento = ["E.C."] + [f"B{i}" for i in range(1, 21)] + ["Finisher"]

tab_general, tab_excepcion, tab_ejercicios = st.tabs(["📅 Pizarra General", "👤 Excepciones", "📚 Catálogo"])

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
        try:
            df_ej = pd.read_sql("SELECT * FROM Ejercicios ORDER BY Nombre", conn)
            st.dataframe(df_ej, use_container_width=True)
        except:
            df_ej = pd.DataFrame()
            st.info("Cargá ejercicios.")

# ==========================================
# PESTAÑA 1: PIZARRA GENERAL
# ==========================================
with tab_general:
    if df_ej.empty:
        st.warning("Primero cargá ejercicios.")
    else:
        dia_sel = st.selectbox("Día:", dias_semana)
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
            try:
                df_gen = pd.read_sql("SELECT RG.*, E.Nombre as Ejercicio FROM Rutina_General RG JOIN Ejercicios E ON RG.IdEjercicio=E.IdEjercicio WHERE DiaSemana=?", conn, params=(dia_sel,))
                if not df_gen.empty:
                    st.dataframe(ordenar_bloques(df_gen)[['Bloque', 'Ejercicio', 'Repeticiones', 'Detalle']], hide_index=True)
            except: st.info("Pizarra vacía.")

# ==========================================
# PESTAÑA 2: EXCEPCIONES
# ==========================================
with tab_excepcion:
    df_socios = pd.read_sql("SELECT IdSocio, Nombre, Apellido FROM Socios WHERE Activo=1", conn)
    if not df_socios.empty:
        socio_sel = st.selectbox("Alumno", df_socios.apply(lambda r: f"{r['IdSocio']} - {r['Nombre']} {r['Apellido']}", axis=1))
        id_socio = int(socio_sel.split(" - ")[0])
        dia_exc = st.selectbox("Día:", dias_semana, key="d_e")
        
        # Formulario Excepcion
        with st.form("form_exc"):
            bloque_exc = st.selectbox("Bloque", bloques_entrenamiento, key="b_e")
            ej_exc = st.selectbox("Ejercicio", df_ej.apply(lambda r: f"{r['IdEjercicio']} - {r['Nombre']}", axis=1), key="e_e")
            reps_exc = st.text_input("Repeticiones (Ej: 10-10-10)", key="r_e")
            det_exc = st.text_input("Detalle", key="det_e")
            if st.form_submit_button("Anotar Excepción"):
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Rutina_Excepcion (IdSocio, DiaSemana, Bloque, IdEjercicio, Repeticiones, Detalle) VALUES (?,?,?,?,?,?)",
                               (id_socio, dia_exc, bloque_exc, int(ej_exc.split(" - ")[0]), reps_exc, det_exc))
                conn.commit()
                st.rerun()
        
        # Lista Excepciones
        df_exc = pd.read_sql("SELECT RE.*, E.Nombre as Ejercicio FROM Rutina_Excepcion RE JOIN Ejercicios E ON RE.IdEjercicio=E.IdEjercicio WHERE IdSocio=? AND DiaSemana=?", conn, params=(id_socio, dia_exc))
        if not df_exc.empty:
            st.dataframe(df_exc[['Bloque', 'Ejercicio', 'Repeticiones', 'Detalle']], hide_index=True)
