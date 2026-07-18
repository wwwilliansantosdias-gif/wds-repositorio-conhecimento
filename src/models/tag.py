"""Modelo do registro armazenado em tabela_tags."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Tag:
    """Representa os campos de uma tag persistida no SQLite."""

    id: int
    nome: str
