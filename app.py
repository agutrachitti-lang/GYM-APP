import streamlit as st
# Cambiamos la dirección de donde busca la función
from database.vencimientos import controlar_vencimientos_automaticos

controlar_vencimientos_automaticos()

st.title("Sistema Administrativo")

import streamlit as st
from database.conexion import controlar_vencimientos_automaticos

# Corremos el control automático apenas arranca el sistema
controlar_vencimientos_automaticos()

st.title("Sistema Administrativo")
st.write("👈 Usá el menú de la izquierda para navegar.")
