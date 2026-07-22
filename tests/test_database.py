"""Testes da infraestrutura de persistência SQLite."""

from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from persistence.database import Database, initialize_database


class DatabaseTests(unittest.TestCase):
    def test_initialize_creates_database_and_initial_tables(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "banco.db"

            initialize_database(database_path)

            self.assertTrue(database_path.is_file())
            with Database(database_path).connection() as connection:
                tables = {
                    row["name"]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    )
                }

            self.assertTrue(
                {
                    "schema_migrations",
                    "tabela_objetos",
                    "tabela_tags",
                    "tabela_objeto_tag",
                    "tabela_relacoes",
                }.issubset(tables)
            )

    def test_initial_schema_contains_architecture_columns(self) -> None:
        expected_columns = {
            "tabela_objetos": {
                "id",
                "titulo",
                "tipo",
                "caminho",
                "resumo",
                "hash_arquivo",
                "status",
                "data_criacao",
                "data_edicao",
                "data_exclusao",
            },
            "tabela_tags": {"id", "nome"},
            "tabela_objeto_tag": {"objeto_id", "tag_id"},
            "tabela_relacoes": {"origem", "destino", "tipo_relacao"},
        }

        with TemporaryDirectory() as temporary_directory:
            database = Database(Path(temporary_directory) / "banco.db")
            database.initialize()

            with database.connection() as connection:
                for table, columns in expected_columns.items():
                    actual_columns = {
                        row["name"]
                        for row in connection.execute(f"PRAGMA table_info({table})")
                    }
                    self.assertEqual(actual_columns, columns)

    def test_migrations_are_applied_only_once(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            database = Database(Path(temporary_directory) / "banco.db")
            database.initialize()
            database.initialize()

            with database.connection() as connection:
                migrations = connection.execute(
                    "SELECT version FROM schema_migrations"
                ).fetchall()

            self.assertEqual([row["version"] for row in migrations], [1, 2])

    def test_connections_enable_foreign_keys(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            database = Database(Path(temporary_directory) / "banco.db")

            with database.connection() as connection:
                foreign_keys_enabled = connection.execute("PRAGMA foreign_keys").fetchone()[0]

            self.assertEqual(foreign_keys_enabled, 1)
