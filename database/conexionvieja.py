import pyodbc
import streamlit as st

@st.cache_resource
def get_connection():
    # Esta es la llave para entrar a tu SQL Server local
    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"
        "DATABASE=GymAdmin;"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(connection_string)

import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

def controlar_vencimientos_automaticos():
    conn = get_connection()
    query = """
        SELECT S.IdSocio, S.FechaVencimiento, S.Saldo, P.Precio, P.DuracionMeses 
        FROM Socios S
        INNER JOIN Planes P ON S.IdPlan = P.IdPlan
        WHERE S.Activo = 1 
    """
    df_activos = pd.read_sql(query, conn)
    hoy = datetime.today().date()
    
    cursor = conn.cursor()
    cambios = False
    
    for index, row in df_activos.iterrows():
        vencimiento = pd.to_datetime(row['FechaVencimiento']).date()
        
        # Si la fecha de vencimiento ya pasó (o es hoy)
        if vencimiento <= hoy:
            saldo = float(row['Saldo'])
            precio = float(row['Precio'])
            meses = int(row['DuracionMeses'])
            
            # Ciclo por si debe más de un mes (ej. no entró al sistema por 3 meses)
            while vencimiento <= hoy:
                saldo -= precio # Genera la deuda
                vencimiento += relativedelta(months=meses) # Patea el vencimiento
            
            # Guardamos la actualización silenciosa
            cursor.execute("UPDATE Socios SET Saldo=?, FechaVencimiento=? WHERE IdSocio=?", 
                           (saldo, vencimiento, row['IdSocio']))
            cambios = True
            
    if cambios:
        conn.commit()