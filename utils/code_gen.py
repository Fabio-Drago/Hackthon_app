# utils/code_gen.py
import random
import string
from models import Room # Importa o modelo para verificar unicidade

def generate_room_code(length=6):
    """Gera um código alfanumérico único para a sala."""
    while True:
        # Gera um código aleatório (letras maiúsculas e dígitos)
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        # Verifica se o código já existe no banco de dados
        existing_room = Room.query.filter_by(code=code).first()
        if not existing_room:
            return code # Retorna o código se for único