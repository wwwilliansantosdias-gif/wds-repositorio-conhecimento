"""Componente-base para serviços que dependem da persistência."""

from __future__ import annotations

from persistence import Database


class BaseService:
    """Mantém a dependência de persistência para serviços futuros."""

    def __init__(self, database: Database) -> None:
        self._database = database

    @property
    def database(self) -> Database:
        """Expõe a infraestrutura de persistência injetada."""
        return self._database
