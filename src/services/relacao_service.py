"""Serviço para criação, remoção e consulta de relações entre objetos."""

from __future__ import annotations

import sqlite3

from models import Relacao
from services.base import BaseService


class RelacaoService(BaseService):
    """Coordena a gravação e consulta de relações no SQLite."""

    def criar(self, origem: int, destino: int, tipo_relacao: str) -> Relacao:
        """Cria uma relação entre dois objetos existentes."""
        if origem == destino:
            raise ValueError("auto-relação não é permitida")

        with self.database.connection() as connection:
            try:
                with connection:
                    connection.execute(
                        """
                        INSERT INTO tabela_relacoes (origem, destino, tipo_relacao)
                        VALUES (?, ?, ?)
                        """,
                        (origem, destino, tipo_relacao),
                    )
            except sqlite3.IntegrityError as error:
                if "FOREIGN KEY constraint failed" in str(error):
                    raise LookupError(
                        "objeto de origem ou destino não encontrado: "
                        f"origem={origem}, destino={destino}"
                    ) from error
                raise

        return Relacao(origem=origem, destino=destino, tipo_relacao=tipo_relacao)

    def remover(self, origem: int, destino: int, tipo_relacao: str) -> None:
        """Remove a relação identificada pelos seus três campos."""
        with self.database.connection() as connection:
            with connection:
                connection.execute(
                    """
                    DELETE FROM tabela_relacoes
                    WHERE origem = ? AND destino = ? AND tipo_relacao = ?
                    """,
                    (origem, destino, tipo_relacao),
                )

    def listar_por_objeto(self, objeto_id: int) -> list[Relacao]:
        """Lista relações em que o objeto é origem ou destino."""
        with self.database.connection() as connection:
            rows = connection.execute(
                """
                SELECT origem, destino, tipo_relacao
                FROM tabela_relacoes
                WHERE origem = ? OR destino = ?
                ORDER BY origem, destino, tipo_relacao
                """,
                (objeto_id, objeto_id),
            ).fetchall()

        return [Relacao(**dict(row)) for row in rows]
