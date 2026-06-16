import streamlit as st
import pandas as pd
from database.conexion import get_connection

st.set_page_config(page_title="Pizarra de Entrenamiento", layout="wide")
st.title("🏋️‍♂️ Pizarra de Entrenamiento")

conn = get_connection()
dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

# Lista expandida: E.C., B1 a B20, Finisher
bloques_entrenamiento = ["E.C. (Entrada en Calor)"] + [f"B{i} (Bloque {i})" for i in range(1, 21)] + ["Finisher"]

tab_general, tab_excepcion, tab_ejercicios = st.tabs(["📅 Pizarra General", "👤 Excepciones por Alumno", "📚 Catálogo de Ejercicios"])

# ==========================================
# PESTAÑA 3: CATÁLOGO DE EJERCICIOS
# ==========================================
with tab_ejercicios:
    col_ej1, col_ej2 = st.columns([1, 2])
    with col_ej1:
        with st.form("form_ejercicio", clear_on_submit=True):
            st.subheader("➕ Agregar Ejercicio al Catálogo")
            st.write("Cargalo una vez y queda para siempre (Ej: Push Press)")
            nombre_ej = st.text_input("Nombre del Ejercicio")
            if st.form_submit_button("Guardar Ejercicio", type="primary"):
                if nombre_ej:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO Ejercicios (Nombre) VALUES (?, ?)", (nombre_ej.strip().title(),))
                        conn.commit()
                        st.success("Guardado.")
                        st.rerun()
                    except:
                        st.error("Ese ejercicio ya está en la lista o hay un error de conexión.")
    
    with col_ej2:
        df_ej = pd.read_sql("SELECT IdEjercicio, Nombre FROM Ejercicios ORDER BY Nombre", conn)
        if not df_ej.empty:
            st.dataframe(df_ej, hide_index=True, use_container_width=True)
        else:
            st.info("Cargá algunos ejercicios para empezar a armar la pizarra.")

# ==========================================
# PESTAÑA 1: PIZARRA GENERAL
# ==========================================
with tab_general:
    if df_ej.empty:
        st.warning("Primero debes cargar ejercicios en el Catálogo.")
    else:
        dia_seleccionado = st.selectbox("📌 Seleccionar Día de la Semana:", dias_semana)
        st.divider()
        
        col_gen_form, col_gen_lista = st.columns([1, 2])
        
        # Formulario estilo Pizarra Dinámico
        with col_gen_form:
            with st.container(border=True):
                st.write(f"**Agregar a la Pizarra del {dia_seleccionado}**")
                
                bloque_sel = st.selectbox("1. Elegir Bloque", bloques_entrenamiento)
                
                opciones_ej = df_ej.apply(lambda r: f"{r['IdEjercicio']} - {r['Nombre']}", axis=1).tolist()
                ej_sel = st.selectbox("2. Elegir Ejercicio", opciones_ej)
                id_ej = int(ej_sel.split(" - ")[0])
                
                # --- LÓGICA DE SERIES VERTICALES Y DINÁMICAS ---
                st.write("**3. Configurar Repeticiones**")
                cant_series = st.number_input("Cantidad de Series", min_value=1, max_value=10, value=3, step=1)
                
                # Dibujamos tantas columnas como series pidió
                cols_series = st.columns(cant_series)
                reps_ingresadas = []
                
                for i in range(cant_series):
                    with cols_series[i]:
                        # Cada cuadrito es para una serie distinta
                        rep = st.text_input(f"S{i+1}", key=f"rep_gen_{i}")
                        reps_ingresadas.append(rep)
                
                detalle = st.text_input("4. Detalle / Aclaración (Ej: 4', c/ barra, 20kg)")
                
                st.write("") # Espacio
                if st.button("➕ Escribir en Pizarra", type="primary", use_container_width=True):
                    # Limpiamos las que quedaron vacías y las unimos con un guion
                    reps_limpias = [r.strip() for r in reps_ingresadas if r.strip() != ""]
                    
                    if len(reps_limpias) > 0:
                        reps_final = "-".join(reps_limpias) # Ej: "15-12-10"
                        
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO Rutina_General (DiaSemana, Bloque, IdEjercicio, Repeticiones, Detalle)
                            VALUES (?, ?, ?, ?, ?)
                        """, (dia_seleccionado, bloque_sel.split(" ")[0], id_ej, reps_final, detalle.strip()))
                        conn.commit()
                        st.rerun()
                    else:
                        st.error("Completá al menos los datos de una serie.")
                        
        # Visualización idéntica a la pizarra
        with col_gen_lista:
            st.subheader(f"📋 Pizarra del {dia_seleccionado}")
            query_gen = """
                SELECT RG.IdRutinaGen, RG.Bloque, E.Nombre as Ejercicio, RG.Repeticiones, RG.Detalle 
                FROM Rutina_General RG
                INNER JOIN Ejercicios E ON RG.IdEjercicio = E.IdEjercicio
                WHERE RG.DiaSemana = ?
                ORDER BY 
                    -- Ordenamos para que E.C. quede primero, luego los B, luego Finisher
                    CASE WHEN RG.Bloque = 'E.C.' THEN 0 
                         WHEN RG.Bloque = 'Finisher' THEN 99 
                         ELSE CAST(SUBSTRING(RG.Bloque, 2, LEN(RG.Bloque)) AS INT) 
                    END ASC, 
                    RG.IdRutinaGen ASC
            """
            df_gen = pd.read_sql(query_gen, conn, params=(dia_seleccionado,))
            
            if not df_gen.empty:
                bloques_cargados = df_gen['Bloque'].unique()
                for b in bloques_cargados:
                    st.markdown(f"#### {b}")
                    df_b = df_gen[df_gen['Bloque'] == b]
                    st.dataframe(df_b[['Ejercicio', 'Repeticiones', 'Detalle']], hide_index=True, use_container_width=True)
                
                st.write("")
                with st.expander("🗑️ Borrar ejercicio de la pizarra"):
                    ej_a_borrar = st.selectbox("Seleccionar para borrar:", df_gen.apply(lambda r: f"{r['IdRutinaGen']} - [{r['Bloque']}] {r['Ejercicio']}", axis=1))
                    if st.button("Borrar línea"):
                        id_borrar = int(ej_a_borrar.split(" - ")[0])
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM Rutina_General WHERE IdRutinaGen=?", (id_borrar,))
                        conn.commit()
                        st.rerun()
            else:
                st.info("La pizarra está en blanco hoy.")

# ==========================================
# PESTAÑA 2: EXCEPCIONES POR ALUMNO
# ==========================================
with tab_excepcion:
    df_socios = pd.read_sql("SELECT IdSocio, Nombre, Apellido, DNI FROM Socios WHERE Activo = 1", conn)
    
    if df_socios.empty or df_ej.empty:
        st.warning("Faltan socios o ejercicios para crear excepciones.")
    else:
        opciones_socios = df_socios.apply(lambda row: f"{row['IdSocio']} - DNI: {row['DNI']} - {row['Nombre']} {row['Apellido']}", axis=1).tolist()
        socio_exc = st.selectbox("🔍 Buscar Alumno:", opciones_socios)
        id_socio_exc = int(socio_exc.split(" - ")[0])
        
        dia_exc = st.selectbox("📌 Seleccionar Día:", dias_semana, key="dia_exc")
        
        st.divider()
        col_exc_form, col_exc_lista = st.columns([1, 2])
        
        with col_exc_form:
            with st.container(border=True):
                st.write("**Anotar Ejercicio Especial**")
                
                bloque_exc = st.selectbox("1. Bloque", bloques_entrenamiento, key="blq_exc")
                ej_sel_exc = st.selectbox("2. Ejercicio Diferente", opciones_ej, key="ej_sel_exc")
                id_ej_exc = int(ej_sel_exc.split(" - ")[0])
                
                st.write("**3. Configurar Repeticiones**")
                cant_series_exc = st.number_input("Cantidad de Series", min_value=1, max_value=10, value=3, step=1, key="cant_s_exc")
                
                cols_series_exc = st.columns(cant_series_exc)
                reps_ingresadas_exc = []
                
                for i in range(cant_series_exc):
                    with cols_series_exc[i]:
                        rep_e = st.text_input(f"S{i+1}", key=f"rep_exc_{i}")
                        reps_ingresadas_exc.append(rep_e)
                
                d_exc = st.text_input("4. Aclaración (Ej: Sin peso)", key="d_exc")
                
                if st.button("➕ Anotar a este alumno", type="primary", use_container_width=True):
                    reps_limpias_exc = [r.strip() for r in reps_ingresadas_exc if r.strip() != ""]
                    
                    if len(reps_limpias_exc) > 0:
                        reps_final_exc = "-".join(reps_limpias_exc)
                        
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO Rutina_Excepcion (IdSocio, DiaSemana, Bloque, IdEjercicio, Repeticiones, Detalle)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (id_socio_exc, dia_exc, bloque_exc.split(" ")[0], id_ej_exc, reps_final_exc, d_exc.strip()))
                        conn.commit()
                        st.rerun()
                    else:
                        st.error("Completá al menos los datos de una serie.")
                        
        with col_exc_lista:
            st.subheader(f"📋 Excepciones de {socio_exc.split(' - ')[2]} ({dia_exc})")
            query_exc = """
                SELECT RE.IdRutinaExc, RE.Bloque, E.Nombre as Ejercicio, RE.Repeticiones, RE.Detalle 
                FROM Rutina_Excepcion RE
                INNER JOIN Ejercicios E ON RE.IdEjercicio = E.IdEjercicio
                WHERE RE.IdSocio = ? AND RE.DiaSemana = ?
                ORDER BY 
                    CASE WHEN RE.Bloque = 'E.C.' THEN 0 
                         WHEN RE.Bloque = 'Finisher' THEN 99 
                         ELSE CAST(SUBSTRING(RE.Bloque, 2, LEN(RE.Bloque)) AS INT) 
                    END ASC, 
                    RE.IdRutinaExc ASC
            """
            df_exc = pd.read_sql(query_exc, conn, params=(id_socio_exc, dia_exc))
            
            if not df_exc.empty:
                st.warning("Anotaciones especiales para este alumno:")
                bloques_exc = df_exc['Bloque'].unique()
                for b in bloques_exc:
                    st.markdown(f"#### {b}")
                    df_b_exc = df_exc[df_exc['Bloque'] == b]
                    st.dataframe(df_b_exc[['Ejercicio', 'Repeticiones', 'Detalle']], hide_index=True, use_container_width=True)
                
                st.write("")
                with st.expander("🗑️ Borrar excepción"):
                    borrar_exc = st.selectbox("Seleccionar:", df_exc.apply(lambda r: f"{r['IdRutinaExc']} - [{r['Bloque']}] {r['Ejercicio']}", axis=1))
                    if st.button("Eliminar Excepción"):
                        id_del_exc = int(borrar_exc.split(" - ")[0])
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM Rutina_Excepcion WHERE IdRutinaExc=?", (id_del_exc,))
                        conn.commit()
                        st.rerun()
            else:
                st.info("Este alumno sigue la Pizarra General sin modificaciones.")