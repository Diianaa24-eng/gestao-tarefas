from dataclasses import dataclass
from datetime import date, time
from typing import Optional

@dataclass
class Utilizador:
    id_utilizador: Optional[int] = None
    nome: str = ""
    email: str = ""
    palavra_passe: str = ""

@dataclass
class Categoria:
    id_categoria: Optional[int] = None
    nome: str = ""
    id_utilizador: int = 0

@dataclass
class Tarefa:
    id_tarefa: Optional[int] = None
    titulo: str = ""
    descricao: str = ""
    data_criacao: Optional[date] = None
    data_limite: Optional[date] = None
    estado: str = "Pendente"
    id_categoria: int = 0
    id_utilizador: int = 0

@dataclass
class Evento:
    id_evento: Optional[int] = None
    titulo: str = ""
    descricao: str = ""
    data_evento: Optional[date] = None
    hora_evento: Optional[time] = None
    local: str = ""
    id_utilizador: int = 0

@dataclass
class Pagamento:
    id_pagamento: Optional[int] = None
    descricao: str = ""
    valor: float = 0.0
    data_pagamento: Optional[date] = None
    estado: str = "Pendente"
    id_utilizador: int = 0
