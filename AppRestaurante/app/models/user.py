# app/models/user.py
class User:
    def __init__(self, id: int, usuario: str, email: str, rol: str):
        self.id = id
        self.usuario = usuario
        self.email = email
        self.rol = rol

    
def get_user_by_credentials(usuario: str, password: str):
    # Esta función ya no se usa si estás consultando al backend externo.
    return None
