"""Testes do NovoObjetoController -- unifica as 4 formas de criar um objeto."""

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
from services.importacao_service import ImportacaoService
from services.objeto_service import ObjetoService
from openpyxl import Workbook

from controllers.novo_objeto_controller import NovoObjetoController


class EmbeddingServiceStub:
    """Substituto do EmbeddingService que evita carregar o modelo real
    (e, portanto, depender de rede) nestes testes, que validam apenas a
    logica de criacao e tratamento de erro -- nao a indexacao semantica
    em si, ja coberta em tests/test_embedding_service.py."""

    def indexar_objeto(self, *args, **kwargs) -> None:
        pass

    def remover_do_indice(self, *args, **kwargs) -> None:
        pass


class NovoObjetoControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        temporary_path = Path(self.temporary_directory.name)

        self.database = Database(temporary_path / "banco.db")
        self.database.initialize()

        self.objeto_service = ObjetoService(self.database)
        self.acervo_service = AcervoService(
            self.objeto_service, EmbeddingServiceStub()
        )

        self.pasta_notas = temporary_path / "acervo" / "notas"
        self.pasta_planilhas = temporary_path / "acervo" / "planilhas"
        self.importacao_service = ImportacaoService(
            self.acervo_service,
            pasta_notas=self.pasta_notas,
            pasta_planilhas=self.pasta_planilhas,
        )
        self.controller = NovoObjetoController(self.importacao_service)

    def tearDown(self) -> None:
        try:
            self.temporary_directory.cleanup()
        except PermissionError:
            pass

    def test_criar_nota_com_sucesso_gera_objeto_e_arquivo_fisico(self) -> None:
        resultado = self.controller.criar_nota("Minha nota")

        self.assertTrue(resultado.sucesso)
        self.assertIsNone(resultado.mensagem_erro)
        self.assertEqual(resultado.objeto.titulo, "Minha nota")
        self.assertEqual(resultado.objeto.tipo, "Nota")

        caminho_esperado = self.pasta_notas / f"{resultado.objeto.id}.md"
        self.assertTrue(caminho_esperado.is_file())

    def test_criar_nota_com_titulo_vazio_retorna_erro_tratado(self) -> None:
        resultado = self.controller.criar_nota("   ")

        self.assertFalse(resultado.sucesso)
        self.assertIsNone(resultado.objeto)
        self.assertIsNotNone(resultado.mensagem_erro)

    def test_cadastrar_link_com_sucesso(self) -> None:
        resultado = self.controller.cadastrar_link(
            "https://exemplo.com/pagina", titulo="Pagina de teste"
        )

        self.assertTrue(resultado.sucesso)
        self.assertEqual(resultado.objeto.tipo, "Link")

    def test_cadastrar_link_duplicado_retorna_erro_tratado(self) -> None:
        self.controller.cadastrar_link("https://exemplo.com/repetido")
        resultado = self.controller.cadastrar_link("https://exemplo.com/repetido")

        self.assertFalse(resultado.sucesso)
        self.assertIn("acervo", resultado.mensagem_erro.lower())

    def test_importar_pdf_inexistente_retorna_erro_tratado_sem_lancar_excecao(
        self,
    ) -> None:
        resultado = self.controller.importar_pdf("/caminho/que/nao/existe.pdf")

        self.assertFalse(resultado.sucesso)
        self.assertEqual(resultado.mensagem_erro, "Arquivo nao encontrado.")

    def test_importar_markdown_inexistente_retorna_erro_tratado(self) -> None:
        resultado = self.controller.importar_markdown("/caminho/que/nao/existe.md")

        self.assertFalse(resultado.sucesso)
        self.assertEqual(resultado.mensagem_erro, "Arquivo nao encontrado.")

    def test_importar_markdown_com_sucesso(self) -> None:
        with TemporaryDirectory() as origem_dir:
            arquivo = Path(origem_dir) / "nota-externa.md"
            arquivo.write_text("Conteudo qualquer.", encoding="utf-8")

            resultado = self.controller.importar_markdown(arquivo)

            self.assertTrue(resultado.sucesso)
            self.assertEqual(resultado.objeto.tipo, "Markdown")

    def test_importar_planilha_com_sucesso(self) -> None:
        with TemporaryDirectory() as origem_dir:
            arquivo = Path(origem_dir) / "dados.xlsx"
            planilha = Workbook()
            planilha.active.append(["Cabecalho", "Conteudo"])
            planilha.save(arquivo)

            resultado = self.controller.importar_planilha(arquivo)

            self.assertTrue(resultado.sucesso)
            self.assertEqual(resultado.objeto.tipo, "Planilha")
            self.assertTrue(
                (self.pasta_planilhas / f"{resultado.objeto.id}.xlsx").is_file()
            )

    def test_resultado_de_erro_nunca_deixa_objeto_criado_pela_metade(self) -> None:
        """Ao falhar, nao deve sobrar nenhum objeto orfao cadastrado."""
        objetos_antes = len(self.acervo_service.listar_ativos())

        self.controller.importar_pdf("/nao/existe.pdf")
        self.controller.criar_nota("")

        objetos_depois = len(self.acervo_service.listar_ativos())
        self.assertEqual(objetos_antes, objetos_depois)


if __name__ == "__main__":
    unittest.main()
