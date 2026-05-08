import bcrypt
from db import criar_utilizador, obter_utilizador_por_email

def hash_password(password: str) -> str:
    """Gera hash seguro da password."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verificar_password(password: str, hashed: str) -> bool:
    """Verifica se a password corresponde ao hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def registar_utilizador(nome: str, email: str, password: str) -> tuple[bool, str]:
    """Regista um novo utilizador."""
    
    existente = obter_utilizador_por_email(email)
    if existente:
        return False, "Este email já está registado."
    
    
    try:
        password_hash = hash_password(password)
        criar_utilizador(nome, email, password_hash)
        return True, "Conta criada com sucesso!"
    except Exception as e:
        return False, f"Erro ao criar conta: {e}"

def autenticar(email: str, password: str) -> tuple[bool, any]:
    """Autentica um utilizador."""
    utilizador = obter_utilizador_por_email(email)
    
    if not utilizador:
        return False, "Email não encontrado."
    
    if verificar_password(password, utilizador['palavra_passe']):
        return True, utilizador
    
    return False, "Password incorreta."
