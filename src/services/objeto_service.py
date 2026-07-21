"""Serviço para cadastro, atualização, consulta e gerenciamento de objetos."""

from __future__ import annotations

from datetime import datetime, timezone
import sqlite3
from typing import Final

from models import Objeto
from services.base import BaseService


class _CampoNaoInformado:
    """Representa um argumento opcional que não foi fornecido."""


_CAMPO_NAO_INFORMADO: Final = _CampoNaoInformado()


class ObjetoService(BaseService):
    """Coordena a gravação e consulta dos metadados de objetos no SQLite."""

    def cadastrar(
        self,
        titulo: str,
        tipo: str,
        *,
        caminho: str | None = None,
        resumo: str | None = None,
        hash_arquivo: str | None = None,
    ) -> Objeto:
        """Cadastra um objeto ativo e devolve seu estado persistido."""
        agora = _agora_utc()

        with self.database.connection() as connection:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO tabela_objetos (
                        titulo,
                        tipo,
                        caminho,
                        resumo,
                        hash_arquivo,
                        status,
                        data_criacao,
                        data_edicao,
                        data_exclusao
                    )
                    VALUES (?, ?, ?, ?, ?, 'ativo', ?, ?, NULL)
                    """,
                    (
                        titulo,
                        tipo,
                        caminho,
                        resumo,
                        hash_arquivo,
                        agora,
                        agora,
                    ),
                )

                objeto_id = cursor.lastrowid

            return _obter_objeto(connection, objeto_id)

    def atualizar(
        self,
        objeto_id: int,
        titulo: str,
        tipo: str,
        *,
        caminho: str | None | _CampoNaoInformado = _CAMPO_NAO_INFORMADO,
        resumo: str | None | _CampoNaoInformado = _CAMPO_NAO_INFORMADO,
        hash_arquivo: str | None | _CampoNaoInformado = _CAMPO_NAO_INFORMADO,
    ) -> Objeto:
        """Atualiza os metadados editáveis de um objeto existente."""
        agora = _agora_utc()

        atualizacoes = [
            "titulo = ?",
            "tipo = ?",
        ]
        valores: list[object] = [
            titulo,
            tipo,
        ]

        for coluna, valor in (
            ("caminho", caminho),
            ("resumo", resumo),
            ("hash_arquivo", hash_arquivo),
        ):
            if valor is not _CAMPO_NAO_INFORMADO:
                atualizacoes.append(f"{coluna} = ?")
                valores.append(valor)

        atualizacoes.append("data_edicao = ?")
        valores.extend((agora, objeto_id))

        with self.database.connection() as connection:
            with connection:
                cursor = connection.execute(
                    f"""
                    UPDATE tabela_objetos
                    SET {", ".join(atualizacoes)}
                    WHERE id = ?
                    """,
                    valores,
                )

                if cursor.rowcount == 0:
                    raise LookupError(
                        f"objeto não encontrado: {objeto_id}"
                    )

            return _obter_objeto(connection, objeto_id)

    def obter_por_id(self, objeto_id: int) -> Objeto:
        """Obtém um objeto pelo seu identificador."""
        with self.database.connection() as connection:
            return _obter_objeto(connection, objeto_id)

    def listar(self) -> list[Objeto]:
        """Lista todos os objetos cadastrados em ordem crescente de identificador."""
        with self.database.connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM tabela_objetos
                ORDER BY id
                """
            ).fetchall()

        return [Objeto(**dict(row)) for row in rows]

    def listar_ativos(self) -> list[Objeto]:
        """Lista objetos ativos em ordem crescente de identificador."""
        with self.database.connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM tabela_objetos
                WHERE status = 'ativo'
                ORDER BY id
                """
            ).fetchall()

        return [Objeto(**dict(row)) for row in rows]

    def listar_lixeira(self) -> list[Objeto]:
        """Lista objetos na lixeira do mais recentemente excluído ao mais antigo."""
        with self.database.connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM tabela_objetos
                WHERE status = 'lixeira'
                ORDER BY data_exclusao DESC
                """
            ).fetchall()

        return [Objeto(**dict(row)) for row in rows]

    def excluir(self, objeto_id: int) -> Objeto:
        """Move um objeto para a lixeira."""
        agora = _agora_utc()

        with self.database.connection() as connection:
            with connection:
                cursor = connection.execute(
                    """
                    UPDATE tabela_objetos
                    SET
                        status = 'lixeira',
                        data_edicao = ?,
                        data_exclusao = ?
                    WHERE id = ?
                    """,
                    (
                        agora,
                        agora,
                        objeto_id,
                    ),
                )

                if cursor.rowcount == 0:
                    raise LookupError(
                        f"objeto não encontrado: {objeto_id}"
                    )

            return _obter_objeto(connection, objeto_id)

    def restaurar(self, objeto_id: int) -> Objeto:
        """Restaura um objeto da lixeira."""
        agora = _agora_utc()

        with self.database.connection() as connection:
            with connection:
                cursor = connection.execute(
                    """
                    UPDATE tabela_objetos
                    SET
                        status = 'ativo',
                        data_edicao = ?,
                        data_exclusao = NULL
                    WHERE id = ?
                    """,
                    (
                        agora,
                        objeto_id,
                    ),
                )

                if cursor.rowcount == 0:
                    raise LookupError(
                        f"objeto não encontrado: {objeto_id}"
                    )

            return _obter_objeto(connection, objeto_id)

    def excluir_definitivamente(self, objeto_id: int) -> None:
        """Remove um objeto da lixeira e todos os vínculos que o referenciam."""
        with self.database.connection() as connection:
            with connection:
                objeto = _obter_objeto(connection, objeto_id)
                if objeto.status != "lixeira":
                    raise ValueError(
                        "objeto ativo não pode ser excluído definitivamente: "
                        f"{objeto_id}"
                    )

                connection.execute(
                    """
                    DELETE FROM tabela_objeto_tag
                    WHERE objeto_id = ?
                    """,
                    (objeto_id,),
                )
                connection.execute(
                    """
                    DELETE FROM tabela_relacoes
                    WHERE origem = ? OR destino = ?
                    """,
                    (objeto_id, objeto_id),
                )
                connection.execute(
                    """
                    DELETE FROM tabela_objetos
                    WHERE id = ?
                    """,
                    (objeto_id,),
                )


def _agora_utc() -> str:
    """Retorna a data e hora atual em UTC no formato ISO 8601."""
    return datetime.now(timezone.utc).isoformat()


def _obter_objeto(
    connection: sqlite3.Connection,
    objeto_id: int | None,
) -> Objeto:
    """Obtém um objeto persistido pelo identificador."""
    if objeto_id is None:
        raise RuntimeError(
            "SQLite não retornou o identificador do objeto cadastrado"
        )

    row = connection.execute(
        """
        SELECT *
        FROM tabela_objetos
        WHERE id = ?
        """,
        (objeto_id,),
    ).fetchone()

    if row is None:
        raise LookupError(
            f"objeto não encontrado: {objeto_id}"
        )

    return Objeto(**dict(row))
