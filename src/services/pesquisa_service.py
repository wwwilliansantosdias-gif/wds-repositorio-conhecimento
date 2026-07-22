"""Servi\u00e7o de busca textual de Objetos de Conhecimento."""

from __future__ import annotations

from models import Objeto
from services.base import BaseService


class PesquisaService(BaseService):
    """Recupera objetos ativos pelo \u00edndice textual FTS5."""

    def buscar_texto(self, termo: str) -> list[Objeto]:
        """Busca t\u00edtulos e resumos com a sintaxe MATCH do FTS5.

        O asterisco final \u00e9 aceito para consultas por prefixo, como
        ``filosof*``. A consulta \u00e9 executada exclusivamente no \u00edndice
        textual, e o filtro de objetos ativos \u00e9 aplicado no SQLite.
        """
        with self.database.connection() as connection:
            rows = connection.execute(
                """
                SELECT objeto.*
                FROM tabela_objetos_fts
                JOIN tabela_objetos AS objeto
                    ON objeto.id = tabela_objetos_fts.rowid
                WHERE tabela_objetos_fts MATCH ?
                    AND objeto.status = 'ativo'
                ORDER BY rank
                """,
                (termo,),
            ).fetchall()

        return [Objeto(**dict(row)) for row in rows]
