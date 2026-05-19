import subprocess
import sys

def install_if_missing(package_name, import_name=None):
    """Instala un paquete si no está disponible en el entorno virtual."""
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"Instalando {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# Dependencias core
install_if_missing("flet")
install_if_missing("pyodbc")
install_if_missing("bcrypt")

# HU-09: Dependencias de reportes y cifrado
install_if_missing("reportlab")
install_if_missing("pycryptodome", "Crypto")

import flet
import pyodbc
import bcrypt
import reportlab
import Crypto
print("All core modules imported successfully")
