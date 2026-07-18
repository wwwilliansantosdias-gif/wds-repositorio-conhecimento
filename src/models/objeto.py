"""Modelo do registro armazenado em tabela_objetos."""

from __future__ import annotations

from dataclasses import dataclass


STATUS_VALIDOS = frozenset({"ativo", "lixeira"})


@dataclass
class Objeto:
    """Representa os campos de um objeto persistido no SQLite."""

    id: int
    titulo: str
    tipo: str
    caminho: str | None
    resumo: str | None
    hash_arquivo: str | None
    status: str
    data_criacao: str
    data_edicao: str
    data_exclusao: str | None

    def __post_init__(self) -> None:
        if self.status not in STATUS_VALIDOS:
            raise ValueError("status deve ser 'ativo' ou 'lixeira'")
