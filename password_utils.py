import bcrypt

def hash_password(password: str) -> str:
    """
    Encripta una contraseña usando bcrypt.
    
    Args:
        password (str): Contraseña en texto plano
        
    Returns:
        str: Contraseña encriptada en formato string
    """
    # Generar salt y hash la contraseña
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su hash.
    
    Args:
        password (str): Contraseña en texto plano a verificar
        hashed_password (str): Hash de la contraseña almacenada en la BD
        
    Returns:
        bool: True si la contraseña es correcta, False en caso contrario
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
