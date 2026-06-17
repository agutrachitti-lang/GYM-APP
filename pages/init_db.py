from database.conexion import get_connection
conn = get_connection()
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS Planes (IdPlan INTEGER PRIMARY KEY AUTOINCREMENT, NombrePlan TEXT, DuracionMeses INTEGER, Precio REAL)")
cursor.execute("CREATE TABLE IF NOT EXISTS Socios (IdSocio INTEGER PRIMARY KEY AUTOINCREMENT, Nombre TEXT, Apellido TEXT, DNI TEXT UNIQUE, IdPlan INTEGER, FechaAlta TEXT, FechaVencimiento TEXT, Saldo REAL, Activo INTEGER DEFAULT 1)")
cursor.execute("CREATE TABLE IF NOT EXISTS Pagos (IdPago INTEGER PRIMARY KEY AUTOINCREMENT, IdSocio INTEGER, Monto REAL, MetodoPago TEXT, FechaPago TEXT)")
conn.commit()
print("Tablas creadas con éxito.")
