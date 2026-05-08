import mysql.connector
from mysql.connector import Error
from configparser import ConfigParser
from contextlib import contextmanager

def carregar_config(ficheiro="config.ini"):
    config = ConfigParser()
    config.read(ficheiro)
    return {
        "host": config.get("database", "host"),
        "user": config.get("database", "user"),
        "password": config.get("database", "password"),
        "database": config.get("database", "database")
    }

@contextmanager
def get_connection():
    """Context manager para conexões à BD."""
    config = carregar_config()
    con = None
    try:
        con = mysql.connector.connect(**config)
        yield con
    finally:
        if con and con.is_connected():
            con.close()

def executar_query(query, params=None, fetch=False, fetchone=False):
    """Executa uma query e retorna resultados se necessário."""
    with get_connection() as con:
        cursor = con.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            return cursor.fetchall()
        if fetchone:
            return cursor.fetchone()
        
        con.commit()
        return cursor.lastrowid

# --- UTILIZADORES ---

def criar_utilizador(nome, email, password_hash):
    query = "INSERT INTO utilizador (nome, email, palavra_passe) VALUES (%s, %s, %s)"
    return executar_query(query, (nome, email, password_hash))

def obter_utilizador_por_email(email):
    query = "SELECT * FROM utilizador WHERE email = %s"
    return executar_query(query, (email,), fetchone=True)

def obter_utilizador_por_id(id_utilizador):
    query = "SELECT * FROM utilizador WHERE id_utilizador = %s"
    return executar_query(query, (id_utilizador,), fetchone=True)

def listar_utilizadores():
    return executar_query("SELECT id_utilizador, nome, email FROM utilizador", fetch=True)

def atualizar_utilizador(id_utilizador, nome, email, password_hash):
    query = """
        UPDATE utilizador 
        SET nome = %s, email = %s, palavra_passe = %s 
        WHERE id_utilizador = %s
    """
    executar_query(query, (nome, email, password_hash, id_utilizador))

def remover_utilizador(id_utilizador):
    queries = [
        ("DELETE FROM tarefa WHERE id_utilizador = %s", (id_utilizador,)),
        ("DELETE FROM evento WHERE id_utilizador = %s", (id_utilizador,)),
        ("DELETE FROM pagamento WHERE id_utilizador = %s", (id_utilizador,)),
        ("DELETE FROM categoria WHERE id_utilizador = %s", (id_utilizador,)),
        ("DELETE FROM utilizador WHERE id_utilizador = %s", (id_utilizador,)),
    ]
    with get_connection() as con:
        cursor = con.cursor()
        for query, params in queries:
            cursor.execute(query, params)
        con.commit()

# --- CATEGORIAS ---

def criar_categoria(nome, id_utilizador):
    query = "INSERT INTO categoria (nome, id_utilizador) VALUES (%s, %s)"
    return executar_query(query, (nome, id_utilizador))

def listar_categorias(id_utilizador=None):
    if id_utilizador:
        return executar_query(
            "SELECT * FROM categoria WHERE id_utilizador = %s",
            (id_utilizador,), fetch=True
        )
    return executar_query("SELECT * FROM categoria", fetch=True)

def atualizar_categoria(id_categoria, nome, id_utilizador):
    query = "UPDATE categoria SET nome = %s, id_utilizador = %s WHERE id_categoria = %s"
    executar_query(query, (nome, id_utilizador, id_categoria))

def remover_categoria(id_categoria):
    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute("DELETE FROM tarefa WHERE id_categoria = %s", (id_categoria,))
        cursor.execute("DELETE FROM categoria WHERE id_categoria = %s", (id_categoria,))
        con.commit()

# --- TAREFAS ---

def criar_tarefa(titulo, descricao, data_limite, estado, id_categoria, id_utilizador):
    query = """
        INSERT INTO tarefa (titulo, descricao, data_criacao, data_limite, estado, id_categoria, id_utilizador)
        VALUES (%s, %s, CURDATE(), %s, %s, %s, %s)
    """
    return executar_query(query, (titulo, descricao, data_limite, estado, id_categoria, id_utilizador))

def listar_tarefas(id_utilizador=None, filtros=None):
    query = "SELECT * FROM tarefa WHERE 1=1"
    params = []
    
    if id_utilizador:
        query += " AND id_utilizador = %s"
        params.append(id_utilizador)
    
    if filtros:
        if filtros.get("estado"):
            query += " AND estado = %s"
            params.append(filtros["estado"])
        if filtros.get("categoria"):
            query += " AND id_categoria = %s"
            params.append(filtros["categoria"])
        if filtros.get("data_inicio"):
            query += " AND data_limite >= %s"
            params.append(filtros["data_inicio"])
        if filtros.get("data_fim"):
            query += " AND data_limite <= %s"
            params.append(filtros["data_fim"])
        if filtros.get("pesquisa"):
            query += " AND (titulo LIKE %s OR descricao LIKE %s)"
            termo = f"%{filtros['pesquisa']}%"
            params.extend([termo, termo])
    
    query += " ORDER BY data_limite ASC"
    return executar_query(query, params, fetch=True)

def atualizar_tarefa(id_tarefa, titulo, descricao, data_limite, estado, id_categoria, id_utilizador):
    query = """
        UPDATE tarefa
        SET titulo = %s, descricao = %s, data_limite = %s, estado = %s, 
            id_categoria = %s, id_utilizador = %s
        WHERE id_tarefa = %s
    """
    executar_query(query, (titulo, descricao, data_limite, estado, id_categoria, id_utilizador, id_tarefa))

def remover_tarefa(id_tarefa):
    executar_query("DELETE FROM tarefa WHERE id_tarefa = %s", (id_tarefa,))

def obter_estatisticas_tarefas(id_utilizador):
    query = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN estado = 'Concluída' THEN 1 ELSE 0 END) as concluidas,
            SUM(CASE WHEN estado = 'Pendente' THEN 1 ELSE 0 END) as pendentes,
            SUM(CASE WHEN estado = 'Em Progresso' THEN 1 ELSE 0 END) as em_progresso,
            SUM(CASE WHEN data_limite < CURDATE() AND estado != 'Concluída' THEN 1 ELSE 0 END) as atrasadas
        FROM tarefa WHERE id_utilizador = %s
    """
    return executar_query(query, (id_utilizador,), fetchone=True)

# --- EVENTOS ---

def criar_evento(titulo, descricao, data_evento, hora_evento, local, id_utilizador):
    query = """
        INSERT INTO evento (titulo, descricao, data_evento, hora_evento, local, id_utilizador)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    return executar_query(query, (titulo, descricao, data_evento, hora_evento, local, id_utilizador))

def listar_eventos(id_utilizador=None):
    if id_utilizador:
        return executar_query(
            "SELECT * FROM evento WHERE id_utilizador = %s ORDER BY data_evento, hora_evento",
            (id_utilizador,), fetch=True
        )
    return executar_query("SELECT * FROM evento ORDER BY data_evento, hora_evento", fetch=True)

def atualizar_evento(id_evento, titulo, descricao, data_evento, hora_evento, local, id_utilizador):
    query = """
        UPDATE evento
        SET titulo = %s, descricao = %s, data_evento = %s, hora_evento = %s, 
            local = %s, id_utilizador = %s
        WHERE id_evento = %s
    """
    executar_query(query, (titulo, descricao, data_evento, hora_evento, local, id_utilizador, id_evento))

def remover_evento(id_evento):
    executar_query("DELETE FROM evento WHERE id_evento = %s", (id_evento,))

# --- PAGAMENTOS ---

def criar_pagamento(descricao, valor, data_pagamento, estado, id_utilizador):
    query = """
        INSERT INTO pagamento (descricao, valor, data_pagamento, estado, id_utilizador)
        VALUES (%s, %s, %s, %s, %s)
    """
    return executar_query(query, (descricao, valor, data_pagamento, estado, id_utilizador))

def listar_pagamentos(id_utilizador=None):
    if id_utilizador:
        return executar_query(
            "SELECT * FROM pagamento WHERE id_utilizador = %s ORDER BY data_pagamento",
            (id_utilizador,), fetch=True
        )
    return executar_query("SELECT * FROM pagamento ORDER BY data_pagamento", fetch=True)

def atualizar_pagamento(id_pagamento, descricao, valor, data_pagamento, estado, id_utilizador):
    query = """
        UPDATE pagamento
        SET descricao = %s, valor = %s, data_pagamento = %s, estado = %s, id_utilizador = %s
        WHERE id_pagamento = %s
    """
    executar_query(query, (descricao, valor, data_pagamento, estado, id_utilizador, id_pagamento))

def remover_pagamento(id_pagamento):
    executar_query("DELETE FROM pagamento WHERE id_pagamento = %s", (id_pagamento,))

def obter_estatisticas_pagamentos(id_utilizador):
    query = """
        SELECT 
            COUNT(*) as total,
            SUM(valor) as valor_total,
            SUM(CASE WHEN estado = 'Pago' THEN valor ELSE 0 END) as valor_pago,
            SUM(CASE WHEN estado = 'Pendente' THEN valor ELSE 0 END) as valor_pendente
        FROM pagamento WHERE id_utilizador = %s
    """
    return executar_query(query, (id_utilizador,), fetchone=True)

# --- CALENDÁRIO ---

def obter_itens_calendario(id_utilizador):
    """Retorna todos os itens ordenados por data."""
    itens = []
    
    # Tarefas
    tarefas = executar_query(
        "SELECT data_limite as data, titulo, estado as info, 'Tarefa' as tipo FROM tarefa WHERE id_utilizador = %s",
        (id_utilizador,), fetch=True
    )
    itens.extend(tarefas)
    
    # Eventos
    eventos = executar_query(
        "SELECT data_evento as data, titulo, hora_evento as info, 'Evento' as tipo FROM evento WHERE id_utilizador = %s",
        (id_utilizador,), fetch=True
    )
    itens.extend(eventos)
    
    # Pagamentos
    pagamentos = executar_query(
        "SELECT data_pagamento as data, descricao as titulo, CONCAT(valor, '€ - ', estado) as info, 'Pagamento' as tipo FROM pagamento WHERE id_utilizador = %s",
        (id_utilizador,), fetch=True
    )
    itens.extend(pagamentos)
    
    # Ordenar por data
    itens.sort(key=lambda x: x['data'] if x['data'] else '9999-99-99')
    return itens

# --- ALERTAS ---

def obter_alertas(id_utilizador, dias=3):
    """Retorna tarefas e pagamentos próximos do prazo."""
    alertas = []
    
    # Tarefas próximas do prazo
    tarefas = executar_query("""
        SELECT titulo, data_limite, 'Tarefa' as tipo
        FROM tarefa 
        WHERE id_utilizador = %s 
        AND estado != 'Concluída'
        AND data_limite BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
        ORDER BY data_limite
    """, (id_utilizador, dias), fetch=True)
    alertas.extend(tarefas)
    
    # Pagamentos pendentes próximos
    pagamentos = executar_query("""
        SELECT descricao as titulo, data_pagamento as data_limite, 'Pagamento' as tipo
        FROM pagamento 
        WHERE id_utilizador = %s 
        AND estado = 'Pendente'
        AND data_pagamento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
        ORDER BY data_pagamento
    """, (id_utilizador, dias), fetch=True)
    alertas.extend(pagamentos)
    
    return alertas
