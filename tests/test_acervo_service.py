"""Testes do AcervoService -- orquestracao entre ObjetoService e EmbeddingService."""

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
from services.acervo_service import AcervoService
from services.embedding_service import EmbeddingService
from services.objeto_service import ObjetoService


class AcervoServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        temporary_path = Path(self.temporary_directory.name)
        self.database = Database(temporary_path / "banco.db")
        self.database.initialize()
        self.objeto_service = ObjetoService(self.database)
        self.embedding_service = EmbeddingService(
            self.database,
            chroma_path=temporary_path / "chroma_db",
        )
        self.acervo = AcervoService(self.objeto_service, self.embedding_service)

    def tearDown(self) -> None:
        del self.embedding_service
        try:
            self.temporary_directory.cleanup()
        except PermissionError:
            # O ChromaDB pode manter arquivos temporarios abertos no Windows.
            pass

    def test_cadastrar_indexa_automaticamente_para_busca_semantica(self) -> None:
        objeto = self.acervo.cadastrar(
            "Cachorro",
            "Nota",
            resumo="Um animal de estimacao leal.",
        )

        encontrados = self.embedding_service.buscar_semantico("cao")

        self.assertEqual(encontrados[0][0].id, objeto.id)

    def test_atualizar_reindexa_com_o_novo_conteudo(self) -> None:
        objeto = self.acervo.cadastrar(
            "Titulo original", "Nota", resumo="Sobre gatos domesticos."
        )

        self.acervo.atualizar(
            objeto.id,
            objeto.titulo,
            objeto.tipo,
            resumo="Sobre astronomia e planetas."
        )

        encontrados = self.embedding_service.buscar_semantico("universo e estrelas")
        self.assertEqual(encontrados[0][0].id, objeto.id)

    def test_excluir_definitivamente_remove_do_indice_semantico(self) -> None:
        objeto = self.acervo.cadastrar(
            "Cachorro", "Nota", resumo="Um animal leal."
        )

        self.acervo.excluir(objeto.id)
        self.acervo.excluir_definitivamente(objeto.id)

        encontrados = self.embedding_service.buscar_semantico("cao")
        self.assertEqual(encontrados, [])

    def test_excluir_mantem_objeto_pesquisavel_apos_restaurar(self) -> None:
        objeto = self.acervo.cadastrar(
            "Cachorro", "Nota", resumo="Um animal leal."
        )

        self.acervo.excluir(objeto.id)
        self.acervo.restaurar(objeto.id)

        encontrados = self.embedding_service.buscar_semantico("cao")
        self.assertEqual(encontrados[0][0].id, objeto.id)


if __name__ == "__main__":
    unittest.main()