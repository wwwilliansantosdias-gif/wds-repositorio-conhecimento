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
from services.acervo_service import AcervoService
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

        self.acervo_service = AcervoService(self.objeto_service, self.embedding_service)

        self.controller = PesquisaController(
            self.pesquisa_service, self.embedding_service, self.acervo_service
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
        self.assertIn("filosofia", resultados[0].trecho)

    def test_objeto_encontrado_pelos_dois_mecanismos_aparece_uma_vez_como_textual(
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
        self.assertIsNone(resultado.score)
        self.assertIsNotNone(resultado.trecho)
        self.assertIn("estoicismo", resultado.trecho)

    def test_resultado_semantico_com_resumo_nao_tem_contexto(self) -> None:
        objeto = self.objeto_service.cadastrar(
            "Filosofia classica",
            "Nota",
            resumo="Disciplina e virtude no cotidiano.",
        )
        self.embedding_service.indexar_objeto(
            objeto.id, objeto.titulo, objeto.resumo
        )

        resultados = self.controller.pesquisar("estoicismo")

        resultado = next(r for r in resultados if r.objeto.id == objeto.id)
        self.assertIsNotNone(resultado.score)
        self.assertIsNone(resultado.trecho)

    def test_resultados_textuais_vem_antes_dos_semanticos(self) -> None:
        apenas_textual = self.objeto_service.cadastrar(
            "Nota comum", "Nota", resumo="tema comum aqui"
        )
        tambem_semantico = self.objeto_service.cadastrar(
            "Outra nota", "Nota", resumo="assunto diferente"
        )
        self.embedding_service.indexar_objeto(
            tambem_semantico.id, tambem_semantico.titulo, tambem_semantico.resumo
        )

        resultados = self.controller.pesquisar("tema comum")

        ids_em_ordem = [r.objeto.id for r in resultados]
        self.assertEqual(ids_em_ordem[0], apenas_textual.id)
        self.assertEqual(ids_em_ordem[1], tambem_semantico.id)

    def test_listar_todos_retorna_vazio_quando_acervo_esta_vazio(self) -> None:
        self.assertEqual(self.controller.listar_todos(), [])

    def test_listar_todos_traz_todos_os_objetos_ativos_sem_score(self) -> None:
        primeiro = self.objeto_service.cadastrar("Primeiro objeto", "Nota")
        segundo = self.objeto_service.cadastrar("Segundo objeto", "Nota")

        resultados = self.controller.listar_todos()

        ids = {r.objeto.id for r in resultados}
        self.assertEqual(ids, {primeiro.id, segundo.id})
        self.assertTrue(all(r.score is None for r in resultados))

    def test_listar_todos_nao_traz_objeto_na_lixeira(self) -> None:
        ativo = self.objeto_service.cadastrar("Fico ativo", "Nota")
        excluido = self.objeto_service.cadastrar("Vou para a lixeira", "Nota")
        self.objeto_service.excluir(excluido.id)

        resultados = self.controller.listar_todos()

        ids = {r.objeto.id for r in resultados}
        self.assertIn(ativo.id, ids)
        self.assertNotIn(excluido.id, ids)

    def test_listar_todos_mostra_o_mais_recente_primeiro(self) -> None:
        mais_antigo = self.objeto_service.cadastrar("Criado primeiro", "Nota")
        mais_recente = self.objeto_service.cadastrar("Criado depois", "Nota")

        resultados = self.controller.listar_todos()

        self.assertEqual(resultados[0].objeto.id, mais_recente.id)
        self.assertEqual(resultados[1].objeto.id, mais_antigo.id)


if __name__ == "__main__":
    unittest.main()
