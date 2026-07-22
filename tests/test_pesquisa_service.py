"""Testes da busca textual com SQLite FTS5."""

from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from persistence import Database
from persistence.database import INITIAL_SCHEMA_STATEMENTS
from services.objeto_service import ObjetoService
from services.pesquisa_service import PesquisaService


class PesquisaServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        database = Database(Path(self.temporary_directory.name) / "banco.db")
        database.initialize()
        self.objeto_service = ObjetoService(database)
        self.service = PesquisaService(database)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_buscar_texto_encontra_objeto_por_titulo(self) -> None:
        objeto = self.objeto_service.cadastrar("Filosofia antiga", "Nota")

        encontrados = self.service.buscar_texto("filosofia")

        self.assertEqual(encontrados, [objeto])

    def test_buscar_texto_encontra_objeto_por_resumo(self) -> None:
        objeto = self.objeto_service.cadastrar(
            "Anota\u00e7\u00e3o",
            "Nota",
            resumo="Introdu\u00e7\u00e3o \u00e0 epistemologia contempor\u00e2nea",
        )

        encontrados = self.service.buscar_texto("epistemologia")

        self.assertEqual(encontrados, [objeto])

    def test_buscar_texto_nao_retorna_objeto_na_lixeira(self) -> None:
        objeto = self.objeto_service.cadastrar("Arquivo reservado", "Nota")
        self.objeto_service.excluir(objeto.id)

        encontrados = self.service.buscar_texto("reservado")

        self.assertEqual(encontrados, [])

    def test_buscar_texto_reflete_atualizacao_de_titulo(self) -> None:
        objeto = self.objeto_service.cadastrar("Rascunho inicial", "Nota")
        self.objeto_service.atualizar(
            objeto.id,
            "Vers\u00e3o definitiva",
            objeto.tipo,
        )

        encontrados = self.service.buscar_texto("definitiva")

        self.assertEqual([encontrado.id for encontrado in encontrados], [objeto.id])

    def test_migration_indexa_objetos_existentes(self) -> None:
        legacy_directory = TemporaryDirectory()
        self.addCleanup(legacy_directory.cleanup)
        database = Database(Path(legacy_directory.name) / "banco.db")

        with database.connection() as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE schema_migrations (
                        version INTEGER PRIMARY KEY,
                        applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                for statement in INITIAL_SCHEMA_STATEMENTS:
                    connection.execute(statement)
                connection.execute(
                    "INSERT INTO schema_migrations (version) VALUES (1)"
                )
                connection.execute(
                    """
                    INSERT INTO tabela_objetos (
                        titulo, tipo, status, data_criacao, data_edicao
                    )
                    VALUES ('Registro legado', 'Nota', 'ativo', '2026-01-01', '2026-01-01')
                    """
                )

        database.initialize()

        encontrados = PesquisaService(database).buscar_texto("legado")

        self.assertEqual([objeto.titulo for objeto in encontrados], ["Registro legado"])


if __name__ == "__main__":
    unittest.main()
