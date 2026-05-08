import re
from datetime import datetime

def validar_email(email: str) -> tuple[bool, str]:
    """Valida formato de email."""
    if not email:
        return False, "Email é obrigatório."
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Formato de email inválido."
    
    return True, ""

def validar_password(password: str) -> tuple[bool, str]:
    """Valida força da password."""
    if not password:
        return False, "Password é obrigatória."
    
    if len(password) < 6:
        return False, "Password deve ter pelo menos 6 caracteres."
    
    return True, ""

def validar_data(data_str: str, formato: str = "%Y-%m-%d") -> tuple[bool, str]:
    """Valida formato de data."""
    if not data_str:
        return False, "Data é obrigatória."
    
    try:
        datetime.strptime(data_str, formato)
        return True, ""
    except ValueError:
        return False, f"Formato de data inválido. Use {formato.replace('%Y', 'AAAA').replace('%m', 'MM').replace('%d', 'DD')}"

def validar_hora(hora_str: str) -> tuple[bool, str]:
    """Valida formato de hora."""
    if not hora_str:
        return False, "Hora é obrigatória."
    
    try:
        datetime.strptime(hora_str, "%H:%M:%S")
        return True, ""
    except ValueError:
        try:
            datetime.strptime(hora_str, "%H:%M")
            return True, ""
        except ValueError:
            return False, "Formato de hora inválido. Use HH:MM ou HH:MM:SS"

def validar_valor(valor_str: str) -> tuple[bool, str]:
    """Valida valor numérico."""
    if not valor_str:
        return False, "Valor é obrigatório."
    
    try:
        valor = float(valor_str.replace(',', '.'))
        if valor < 0:
            return False, "Valor não pode ser negativo."
        return True, ""
    except ValueError:
        return False, "Valor deve ser um número."

def validar_campos_obrigatorios(**campos) -> tuple[bool, str]:
    """Valida se todos os campos obrigatórios estão preenchidos."""
    vazios = [nome for nome, valor in campos.items() if not valor or not str(valor).strip()]
    
    if vazios:
        return False, f"Campos obrigatórios: {', '.join(vazios)}"
    
    return True, ""
