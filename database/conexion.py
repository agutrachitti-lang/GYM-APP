import streamlit as st
import libsql_experimental as sqlite3

def get_connection():
    db_url = st.secrets["TURSO_DATABASE_URL"]
    auth_token = st.secrets["TURSO_AUTH_TOKEN"]
    
    # Conectamos con el driver que usabas originalmente
    conn = sqlite3.connect(database=db_url, auth_token=auth_token)
    conn.check_same_thread = False
    return conn
