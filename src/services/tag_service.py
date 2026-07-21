"""Serviço para cadastro e associação de tags."""

from __future__ import annotations

import sqlite3

from models import Tag
from services.base import BaseService


class TagService(BaseService):
    """Coordena a gravação e consulta de tags no SQLite."""

    def criar(self, nome: str) -> Tag:
        """Cadastra uma tag e devolve seu estado persistido."""
        with self.database.connection() as connection:
            with connection:
                existente = connection.execute(
                    """
                    SELECT id
                    FROM tabela_tags
                    WHERE nome = ?
                    """,
                    (nome,),
                ).fetchone()

                if existente is not None:
                    raise ValueError(f"tag já cadastrada: {nome}")

                cursor = connection.execute(
                    """
                    INSERT INTO tabela_tags (nome)
                    VALUES (?)
                    """,
                    (nome,),
                )

            return _obter_tag(connection, cursor.lastrowid)

    def listar(self) -> list[Tag]:
        """Lista todas as tags cadastradas em ordem alfabética de nome."""
        with self.database.connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM tabela_tags
                ORDER BY nome
                """
            ).fetchall()

        return [Tag(**dict(row)) for row in rows]

    def associar(self, objeto_id: int, tag_id: int) -> None:
        """Associa uma tag a um objeto existente."""
        with self.database.connection() as connection:
            try:
                with connection:
                    connection.execute(
                        """
                        INSERT INTO tabela_objeto_tag (objeto_id, tag_id)
                        VALUES (?, ?)
                        """,
                        (objeto_id, tag_id),
                    )
            except sqlite3.IntegrityError as error:
                if "FOREIGN KEY constraint failed" in str(error):
                    raise LookupError(
                        "objeto ou tag não encontrado: "
                        f"objeto_id={objeto_id}, tag_id={tag_id}"
                    ) from error
                raise

    def desassociar(self, objeto_id: int, tag_id: int) -> None:
        """Remove a associação entre uma tag e um objeto."""
        with self.database.connection() as connection:
            with connection:
                connection.execute(
                    """
                    DELETE FROM tabela_objeto_tag
                    WHERE objeto_id = ? AND tag_id = ?
                    """,
                    (objeto_id, tag_id),
                )

    def listar_por_objeto(self, objeto_id: int) -> list[Tag]:
        """Lista as tags associadas a um objeto em ordem alfabética de nome."""
        with self.database.connection() as connection:
            rows = connection.execute(
                """
                SELECT tabela_tags.*
                FROM tabela_tags
                INNER JOIN tabela_objeto_tag
                    ON tabela_objeto_tag.tag_id = tabela_tags.id
                WHERE tabela_objeto_tag.objeto_id = ?
                ORDER BY tabela_tags.nome
                """,
                (objeto_id,),
            ).fetchall()

        return [Tag(**dict(row)) for row in rows]


def _obter_tag(
    connection: sqlite3.Connection,
    tag_id: int | None,
) -> Tag:
    """Obtém uma tag persistida pelo identificador."""
    if tag_id is None:
        raise RuntimeError(
            "SQLite não retornou o identificador da tag cadastrada"
        )

    row = connection.execute(
        """
        SELECT *
        FROM tabela_tags
        WHERE id = ?
        """,
        (tag_id,),
    ).fetchone()

    if row is None:
        raise LookupError(f"tag não encontrada: {tag_id}")

    return Tag(**dict(row))
