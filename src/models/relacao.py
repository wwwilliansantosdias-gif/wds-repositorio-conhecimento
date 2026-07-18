"""Modelo do registro armazenado em tabela_relacoes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Relacao:
    """Representa os campos de uma relação entre objetos."""

    origem: int
    destino: int
    tipo_relacao: str
