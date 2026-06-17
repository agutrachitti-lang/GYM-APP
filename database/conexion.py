import streamlit as st
import libsql_experimental as sqlite3

def get_connection():
    # URL y Token que me pasaste
    db_url = "libsql://gymdb-agutrachitti-lang.aws-us-east-1.turso.io"
    auth_token = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODE3MTkyNDEsImlkIjoiMDE5ZWQ2YmMtNzAwMS03MzEzLTllOGYtNzcyMjE2NTU3ZmU0IiwicmlkIjoiMTVlNjFkYzUtMGQzYS00ODc1LTg3OWQtMTA0OTMyOTU0ZGZkIn0.Q-6OhbsrqfuHz4ROTrpNVZXNTfCKQM1Jl9FykIsVSVsb2LVyoTY23n6zsoA95GhSS0HAEPkeMZJAdfcMg3deDw"
    
    # Abrimos la conexión directamente con esos datos
    conn = sqlite3.connect(database=db_url, auth_token=auth_token)
    conn.check_same_thread = False
    
    return conn
