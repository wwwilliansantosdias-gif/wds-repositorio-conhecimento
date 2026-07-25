"""Testes do EditorMarkdownController -- carregar e salvar Notas."""

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

from controllers.editor_markdown_controller import EditorMarkdownController


class EmbeddingServiceStub:
    """Substituto do EmbeddingService que evita carregar o modelo real
    (e depender de rede) nestes testes, focados em carregar/salvar
    arquivo, nao em busca semantica."""

    def indexar_objeto(self, *args, **kwargs) -> None:
        pass

    def remover_do_indice(self, *args, **kwargs) -> None:
        pass


class EditorMarkdownControllerTests(unittest.TestCase):
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
        self.importacao_service = ImportacaoService(
            self.acervo_service, pasta_notas=self.pasta_notas
        )
        self.controller = EditorMarkdownController(self.acervo_service)

    def tearDown(self) -> None:
        try:
            self.temporary_directory.cleanup()
        except PermissionError:
            pass

    def test_carregar_le_o_conteudo_fisico_correto(self) -> None:
        objeto = self.importacao_service.criar_nota_manual(
            "Minha Nota", conteudo="Texto original"
        )

        conteudo = self.controller.carregar(objeto.id)

        self.assertEqual(conteudo.texto, "Texto original")
        self.assertEqual(conteudo.objeto.id, objeto.id)

    def test_salvar_atualiza_arquivo_fisico_e_resumo(self) -> None:
        objeto = self.importacao_service.criar_nota_manual("Nota", conteudo="v1")

        resultado = self.controller.salvar(objeto.id, "v2")

        self.assertTrue(resultado.sucesso)
        self.assertEqual(resultado.objeto.resumo, "v2")
        self.assertEqual(
            Path(objeto.caminho).read_text(encoding="utf-8"), "v2"
        )

    def test_salvar_nao_deixa_arquivo_temporario_para_tras(self) -> None:
        objeto = self.importacao_service.criar_nota_manual("Nota", conteudo="v1")

        self.controller.salvar(objeto.id, "v2")

        arquivos_tmp = list(self.pasta_notas.glob("*.tmp"))
        self.assertEqual(arquivos_tmp, [])

    def test_conteudo_editado_persiste_entre_carregamentos(self) -> None:
        objeto = self.importacao_service.criar_nota_manual("Nota", conteudo="v1")
        self.controller.salvar(objeto.id, "v2")

        conteudo = self.controller.carregar(objeto.id)

        self.assertEqual(conteudo.texto, "v2")

    def test_carregar_recusa_tipo_nao_editavel(self) -> None:
        link = self.objeto_service.cadastrar(
            "Um link", "Link", caminho="https://exemplo.com"
        )

        with self.assertRaises(ValueError):
            self.controller.carregar(link.id)

    def test_salvar_recusa_tipo_nao_editavel_sem_lancar_excecao(self) -> None:
        link = self.objeto_service.cadastrar(
            "Um link", "Link", caminho="https://exemplo.com"
        )

        resultado = self.controller.salvar(link.id, "texto qualquer")

        self.assertFalse(resultado.sucesso)
        self.assertIsNotNone(resultado.mensagem_erro)

    def test_carregar_objeto_inexistente_lanca_lookup_error(self) -> None:
        with self.assertRaises(LookupError):
            self.controller.carregar(99999)

    def test_salvar_objeto_inexistente_retorna_erro_tratado(self) -> None:
        resultado = self.controller.salvar(99999, "texto")

        self.assertFalse(resultado.sucesso)
        self.assertIsNotNone(resultado.mensagem_erro)


if __name__ == "__main__":
    unittest.main()
