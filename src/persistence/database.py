"""Infraestrutura SQLite e migrações do repositório."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
import sqlite3


DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[2] / "banco.db"

INITIAL_SCHEMA_STATEMENTS = (
    """
    CREATE TABLE tabela_objetos (
        id INTEGER PRIMARY KEY,
        titulo TEXT NOT NULL,
        tipo TEXT NOT NULL,
        caminho TEXT,
        resumo TEXT,
        hash_arquivo TEXT,
        status TEXT NOT NULL CHECK (status IN ('ativo', 'lixeira')),
        data_criacao TEXT NOT NULL,
        data_edicao TEXT NOT NULL,
        data_exclusao TEXT
    )
    """,
    """
    CREATE TABLE tabela_tags (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE tabela_objeto_tag (
        objeto_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY (objeto_id, tag_id),
        FOREIGN KEY (objeto_id) REFERENCES tabela_objetos(id),
        FOREIGN KEY (tag_id) REFERENCES tabela_tags(id)
    )
    """,
    """
    CREATE TABLE tabela_relacoes (
        origem INTEGER NOT NULL,
        destino INTEGER NOT NULL,
        tipo_relacao TEXT NOT NULL,
        PRIMARY KEY (origem, destino, tipo_relacao),
        FOREIGN KEY (origem) REFERENCES tabela_objetos(id),
        FOREIGN KEY (destino) REFERENCES tabela_objetos(id)
    )
    """,
)

FTS5_SCHEMA_STATEMENTS = (
    """
    CREATE VIRTUAL TABLE tabela_objetos_fts USING fts5(
        titulo,
        resumo,
        content='tabela_objetos',
        content_rowid='id',
        tokenize='unicode61 remove_diacritics 2',
        prefix='2 3 4'
    )
    """,
    """
    INSERT INTO tabela_objetos_fts (rowid, titulo, resumo)
    SELECT id, titulo, resumo
    FROM tabela_objetos
    """,
    """
    CREATE TRIGGER tabela_objetos_fts_after_insert
    AFTER INSERT ON tabela_objetos
    BEGIN
        INSERT INTO tabela_objetos_fts (rowid, titulo, resumo)
        VALUES (NEW.id, NEW.titulo, NEW.resumo);
    END
    """,
    """
    CREATE TRIGGER tabela_objetos_fts_after_update
    AFTER UPDATE OF titulo, resumo ON tabela_objetos
    BEGIN
        INSERT INTO tabela_objetos_fts (
            tabela_objetos_fts,
            rowid,
            titulo,
            resumo
        )
        VALUES ('delete', OLD.id, OLD.titulo, OLD.resumo);
        INSERT INTO tabela_objetos_fts (rowid, titulo, resumo)
        VALUES (NEW.id, NEW.titulo, NEW.resumo);
    END
    """,
    """
    CREATE TRIGGER tabela_objetos_fts_after_delete
    AFTER DELETE ON tabela_objetos
    BEGIN
        INSERT INTO tabela_objetos_fts (
            tabela_objetos_fts,
            rowid,
            titulo,
            resumo
        )
        VALUES ('delete', OLD.id, OLD.titulo, OLD.resumo);
    END
    """,
)

MIGRATIONS = (
    (1, INITIAL_SCHEMA_STATEMENTS),
    (2, FTS5_SCHEMA_STATEMENTS),
)


class Database:
    """Fornece conexões SQLite e aplica as migrações conhecidas."""

    def __init__(self, path: Path | str = DEFAULT_DATABASE_PATH) -> None:
        self.path = Path(path)

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Abre uma conexão com integridade referencial habilitada."""
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        """Cria o arquivo do banco, quando ausente, e aplica as migrações."""
        with self.connection() as connection:
            _apply_migrations(connection)


def initialize_database(path: Path | str = DEFAULT_DATABASE_PATH) -> None:
    """Inicializa o banco principal ou o caminho SQLite informado."""
    Database(path).initialize()


def _apply_migrations(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    for version, statements in MIGRATIONS:
        applied = connection.execute(
            "SELECT 1 FROM schema_migrations WHERE version = ?", (version,)
        ).fetchone()
        if applied is not None:
            continue

        with connection:
            for statement in statements:
                connection.execute(statement)
            connection.execute(
                "INSERT INTO schema_migrations (version) VALUES (?)", (version,)
            )
