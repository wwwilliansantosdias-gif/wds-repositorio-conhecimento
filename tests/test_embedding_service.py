"""Testes da indexação e busca semântica com ChromaDB."""

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
from services.embedding_service import EmbeddingService
from services.objeto_service import ObjetoService


class EmbeddingServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        temporary_path = Path(self.temporary_directory.name)
        database = Database(temporary_path / "banco.db")
        database.initialize()
        self.objeto_service = ObjetoService(database)
        self.service = EmbeddingService(
            database,
            chroma_path=temporary_path / "chroma_db",
        )

    def tearDown(self) -> None:
        del self.service
        try:
            self.temporary_directory.cleanup()
        except PermissionError:
            # O ChromaDB pode manter arquivos temporários abertos no Windows.
            pass

    def test_indexar_e_buscar_encontra_objeto_por_significado(self) -> None:
        cachorro = self.objeto_service.cadastrar("Cachorro", "Nota")
        meteorologia = self.objeto_service.cadastrar("Previsão do tempo", "Nota")
        self.service.indexar_objeto(cachorro.id, cachorro.titulo, cachorro.resumo)
        self.service.indexar_objeto(
            meteorologia.id,
            meteorologia.titulo,
            meteorologia.resumo,
        )

        encontrados = self.service.buscar_semantico("cão")

        self.assertEqual(encontrados[0][0].id, cachorro.id)
        self.assertIsInstance(encontrados[0][1], float)
        self.assertGreaterEqual(encontrados[0][1], 0)
        self.assertLessEqual(encontrados[0][1], 100)

    def test_busca_nao_retorna_objeto_na_lixeira(self) -> None:
        objeto = self.objeto_service.cadastrar("Cachorro", "Nota")
        self.service.indexar_objeto(objeto.id, objeto.titulo, objeto.resumo)
        self.objeto_service.excluir(objeto.id)

        encontrados = self.service.buscar_semantico("cão")

        self.assertEqual(encontrados, [])

    def test_remover_do_indice_remove_objeto_dos_resultados(self) -> None:
        objeto = self.objeto_service.cadastrar("Cachorro", "Nota")
        self.service.indexar_objeto(objeto.id, objeto.titulo, objeto.resumo)
        self.service.remover_do_indice(objeto.id)

        encontrados = self.service.buscar_semantico("cão")

        self.assertEqual(encontrados, [])


if __name__ == "__main__":
    unittest.main()
