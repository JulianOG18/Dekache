import pyodbc

# Configuración de la base de datos
DB_CONFIG = {
    'driver': '{SQL Server}',
    'server': 'DESKTOP-3ING46S\SQLEXPRESS',  # Cambia si es diferente
    'database': 'DekacheDB',
    'trusted_connection': 'yes'  # Para autenticación de Windows
}

def get_db_connection():
    conn_str = f"DRIVER={DB_CONFIG['driver']};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};Trusted_Connection={DB_CONFIG['trusted_connection']};"
    return pyodbc.connect(conn_str)

def validate_user(correo, contrasena):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT rol FROM Usuarios WHERE correo = ? AND contrasena = ?", (correo, contrasena))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0].capitalize()  # Capitalizar para coincidir con las vistas
        else:
            return None
    except Exception as e:
        print(f"Error de base de datos: {e}")
        return None