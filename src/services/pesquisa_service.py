"""Serviço de busca textual de Objetos de Conhecimento."""

from __future__ import annotations

import re
import sqlite3

from models import Objeto
from services.base import BaseService


class PesquisaService(BaseService):
    """Recupera objetos ativos pelo índice textual FTS5."""

    _PALAVRAS_RESERVADAS = {"AND", "OR", "NOT", "NEAR"}

    def _normalizar_termo_fts(self, termo: str) -> str:
        """Converte texto livre em uma consulta FTS5 segura.

        Preserva apenas o asterisco final como busca por prefixo.
        Todo o restante é tratado como texto literal.
        """
        termo = termo.strip()

        if not termo:
            return ""

        # Remove aspas e parênteses que quebram o parser do FTS5.
        termo = termo.replace('"', "")
        termo = termo.replace("(", " ")
        termo = termo.replace(")", " ")

        tokens: list[str] = []

        for token in termo.split():
            preservar_prefixo = token.endswith("*")

            if preservar_prefixo:
                token = token[:-1]

            # Mantém apenas letras, números e "_".
            token = re.sub(r"[^\w]", " ", token)
            partes = [p for p in token.split() if p]

            for parte in partes:
                if parte.upper() in self._PALAVRAS_RESERVADAS:
                    parte = f'"{parte}"'

                if preservar_prefixo:
                    parte += "*"

                tokens.append(parte)

        return " ".join(tokens)

    def buscar_texto(self, termo: str) -> list[tuple[Objeto, str | None]]:
        """Busca títulos, resumos e tags de objetos ativos."""

        consulta_fts = self._normalizar_termo_fts(termo)

        with self.database.connection() as connection:
            try:
                rows = connection.execute(
                    """
                    WITH resultados AS (
                        SELECT
                            objeto.id AS objeto_id,
                            rank AS ordenacao,
                            0 AS prioridade,
                            snippet(tabela_objetos_fts, -1, '', '', '...', 20)
                                AS trecho
                        FROM tabela_objetos_fts
                        JOIN tabela_objetos AS objeto
                            ON objeto.id = tabela_objetos_fts.rowid
                        WHERE tabela_objetos_fts MATCH ?
                            AND objeto.status = 'ativo'

                        UNION ALL

                        SELECT
                            objeto.id AS objeto_id,
                            0 AS ordenacao,
                            1 AS prioridade,
                            NULL AS trecho
                        FROM tabela_tags AS tag
                        JOIN tabela_objeto_tag AS objeto_tag
                            ON objeto_tag.tag_id = tag.id
                        JOIN tabela_objetos AS objeto
                            ON objeto.id = objeto_tag.objeto_id
                        WHERE tag.nome = ? COLLATE NOCASE
                            AND objeto.status = 'ativo'
                    ),
                    resultados_ranqueados AS (
                        SELECT
                            objeto_id,
                            ordenacao,
                            prioridade,
                            trecho,
                            ROW_NUMBER() OVER (
                                PARTITION BY objeto_id
                                ORDER BY prioridade, ordenacao
                            ) AS posicao
                        FROM resultados
                    )
                    SELECT objeto.*, resultados_ranqueados.trecho
                    FROM resultados_ranqueados
                    JOIN tabela_objetos AS objeto
                        ON objeto.id = resultados_ranqueados.objeto_id
                    WHERE resultados_ranqueados.posicao = 1
                    ORDER BY
                        resultados_ranqueados.prioridade,
                        resultados_ranqueados.ordenacao
                    """,
                    (consulta_fts, termo),
                ).fetchall()

            except sqlite3.OperationalError:
                # Se a consulta FTS ainda for inválida por qualquer motivo,
                # retorna apenas resultados por tag em vez de lançar exceção.
                rows = connection.execute(
                    """
                    SELECT objeto.*, NULL AS trecho
                    FROM tabela_tags AS tag
                    JOIN tabela_objeto_tag AS objeto_tag
                        ON objeto_tag.tag_id = tag.id
                    JOIN tabela_objetos AS objeto
                        ON objeto.id = objeto_tag.objeto_id
                    WHERE tag.nome = ? COLLATE NOCASE
                        AND objeto.status = 'ativo'
                    ORDER BY objeto.titulo
                    """,
                    (termo,),
                ).fetchall()

        resultados: list[tuple[Objeto, str | None]] = []
        for row in rows:
            dados_objeto = dict(row)
            trecho = dados_objeto.pop("trecho")
            resultados.append((Objeto(**dados_objeto), trecho))

        return resultados
