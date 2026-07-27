"""Servi\u00e7o de busca textual de Objetos de Conhecimento."""

from __future__ import annotations

from models import Objeto
from services.base import BaseService


class PesquisaService(BaseService):
    """Recupera objetos ativos pelo \u00edndice textual FTS5."""

    def buscar_texto(self, termo: str) -> list[Objeto]:
        """Busca t\u00edtulos, resumos e tags de objetos ativos.

        O asterisco final \u00e9 aceito para consultas por prefixo, como
        ``filosof*``. T\u00edtulos e resumos usam o \u00edndice FTS5; as tags
        usam as associa\u00e7\u00f5es existentes no SQLite.
        """
        with self.database.connection() as connection:
            rows = connection.execute(
                """
                WITH resultados AS (
                    SELECT
                        objeto.id AS objeto_id,
                        rank AS ordenacao,
                        0 AS prioridade
                    FROM tabela_objetos_fts
                    JOIN tabela_objetos AS objeto
                        ON objeto.id = tabela_objetos_fts.rowid
                    WHERE tabela_objetos_fts MATCH ?
                        AND objeto.status = 'ativo'

                    UNION ALL

                    SELECT
                        objeto.id AS objeto_id,
                        0 AS ordenacao,
                        1 AS prioridade
                    FROM tabela_tags AS tag
                    JOIN tabela_objeto_tag AS objeto_tag
                        ON objeto_tag.tag_id = tag.id
                    JOIN tabela_objetos AS objeto
                        ON objeto.id = objeto_tag.objeto_id
                    WHERE tag.nome = ? COLLATE NOCASE
                        AND objeto.status = 'ativo'
                ),
                objetos_encontrados AS (
                    SELECT
                        objeto_id,
                        MIN(prioridade) AS prioridade,
                        MIN(ordenacao) AS ordenacao
                    FROM resultados
                    GROUP BY objeto_id
                )
                SELECT objeto.*
                FROM objetos_encontrados
                JOIN tabela_objetos AS objeto
                    ON objeto.id = objetos_encontrados.objeto_id
                ORDER BY objetos_encontrados.prioridade, objetos_encontrados.ordenacao
                """,
                (termo, termo),
            ).fetchall()

        return [Objeto(**dict(row)) for row in rows]
