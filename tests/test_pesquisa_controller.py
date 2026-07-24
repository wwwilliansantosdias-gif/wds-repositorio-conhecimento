"""Testes do PesquisaController -- combinacao de busca textual e semantica."""

from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
UI_DIRECTORY = SOURCE_DIRECTORY / "ui"
for caminho in (SOURCE_DIRECTORY, UI_DIRECTORY):
    if str(caminho) not in sys.path:
        sys.path.insert(0, str(caminho))

from persistence import Database
from services.embedding_service import EmbeddingService
from services.objeto_service import ObjetoService
from services.pesquisa_service import PesquisaService

from controllers.pesquisa_controller import PesquisaController


class PesquisaControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        temporary_path = Path(self.temporary_directory.name)

        self.database = Database(temporary_path / "banco.db")
        self.database.initialize()

        self.objeto_service = ObjetoService(self.database)
        self.pesquisa_service = PesquisaService(self.database)

        # Construcao normal, carregando o modelo real -- este controller
        # precisa gerar embeddings novos a partir do termo de busca
        # (buscar_semantico), diferente de ObjetoController.
        self.embedding_service = EmbeddingService(
            self.database,
            chroma_path=temporary_path / "chroma_db",
        )

        self.controller = PesquisaController(
            self.pesquisa_service, self.embedding_service
        )

    def tearDown(self) -> None:
        del self.embedding_service
        try:
            self.temporary_directory.cleanup()
        except PermissionError:
            # O ChromaDB pode manter arquivos temporarios abertos no Windows.
            pass

    def test_termo_vazio_retorna_lista_vazia(self) -> None:
        self.assertEqual(self.controller.pesquisar(""), [])
        self.assertEqual(self.controller.pesquisar("   "), [])

    def test_objeto_encontrado_apenas_por_texto_nao_tem_score(self) -> None:
        objeto = self.objeto_service.cadastrar(
            "Anotacao sobre filosofia", "Nota", resumo="conteudo qualquer"
        )
        # Nao indexado no ChromaDB -- so a busca textual encontra.

        resultados = self.controller.pesquisar("filosofia")

        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0].objeto.id, objeto.id)
        self.assertIsNone(resultados[0].score)

    def test_objeto_encontrado_pelos_dois_mecanismos_aparece_uma_vez_com_score(
        self,
    ) -> None:
        objeto = self.objeto_service.cadastrar(
            "Sobre estoicismo", "Nota", resumo="Epicteto e a aceitacao"
        )
        self.embedding_service.indexar_objeto(
            objeto.id, objeto.titulo, objeto.resumo
        )

        resultados = self.controller.pesquisar("estoicismo")

        ids = [r.objeto.id for r in resultados]
        self.assertEqual(ids.count(objeto.id), 1, "objeto nao pode duplicar na lista")
        resultado = next(r for r in resultados if r.objeto.id == objeto.id)
        self.assertIsNotNone(resultado.score)

    def test_resultados_semanticos_vem_antes_dos_apenas_textuais(self) -> None:
        apenas_textual = self.objeto_service.cadastrar(
            "Nota comum", "Nota", resumo="tema comum aqui"
        )
        tambem_semantico = self.objeto_service.cadastrar(
            "Outra nota", "Nota", resumo="tema comum tambem"
        )
        self.embedding_service.indexar_objeto(
            tambem_semantico.id, tambem_semantico.titulo, tambem_semantico.resumo
        )

        resultados = self.controller.pesquisar("tema comum")

        ids_em_ordem = [r.objeto.id for r in resultados]
        self.assertEqual(ids_em_ordem[0], tambem_semantico.id)
        self.assertIn(apenas_textual.id, ids_em_ordem)


if __name__ == "__main__":
    unittest.main()
