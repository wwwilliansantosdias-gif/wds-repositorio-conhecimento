"""Testes do RelacaoController."""

from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
UI_DIRECTORY = SOURCE_DIRECTORY / "ui"
for caminho in (SOURCE_DIRECTORY, UI_DIRECTORY):
    if str(caminho) not in sys.path:
        sys.path.insert(0, str(caminho))

from models import Objeto
from persistence import Database
from services.acervo_service import AcervoService
from services.importacao_service import ImportacaoService
from services.objeto_service import ObjetoService
from services.pesquisa_service import PesquisaService
from services.relacao_service import RelacaoService

from controllers.novo_objeto_controller import NovoObjetoController
from controllers.relacao_controller import RelacaoController


def criar_objeto_falso(objeto_id: int, titulo: str) -> Objeto:
    return Objeto(
        id=objeto_id,
        titulo=titulo,
        tipo="Nota",
        caminho=None,
        resumo=None,
        hash_arquivo=None,
        status="ativo",
        data_criacao="2026-01-01",
        data_edicao="2026-01-01",
        data_exclusao=None,
    )


class EmbeddingServiceStub:
    """Evita carregar o modelo semântico neste teste de controller."""

    def indexar_objeto(self, *args, **kwargs) -> None:
        pass

    def remover_do_indice(self, *args, **kwargs) -> None:
        pass


class RelacaoControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        database = Database(Path(self.temporary_directory.name) / "banco.db")
        database.initialize()
        self.objeto_service = ObjetoService(database)
        self.relacao_service = RelacaoService(database)
        self.pesquisa_service = Mock(spec=PesquisaService)
        self.acervo_service = AcervoService(self.objeto_service, EmbeddingServiceStub())
        self.novo_objeto_controller = NovoObjetoController(
            ImportacaoService(
                self.acervo_service,
                pasta_notas=Path(self.temporary_directory.name) / "acervo" / "notas",
            )
        )
        self.controller = RelacaoController(
            self.relacao_service,
            self.pesquisa_service,
            self.novo_objeto_controller,
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_buscar_objetos_para_relacionar_exclui_objeto_em_foco(self) -> None:
        em_foco = criar_objeto_falso(1, "Em foco")
        outro = criar_objeto_falso(2, "Outro")
        self.pesquisa_service.buscar_texto.return_value = [
            (em_foco, "trecho"),
            (outro, None),
        ]

        resultado = self.controller.buscar_objetos_para_relacionar("nota", 1)

        self.assertEqual(resultado, [outro])
        self.pesquisa_service.buscar_texto.assert_called_once_with("nota")

    def test_criar_com_tipo_vazio_retorna_erro_tratado(self) -> None:
        resultado = self.controller.criar(1, 2, "   ")

        self.assertFalse(resultado.sucesso)
        self.assertIsNotNone(resultado.mensagem_erro)

    def test_criar_auto_relacao_retorna_erro_tratado(self) -> None:
        objeto = self.objeto_service.cadastrar("Nota", "Nota")

        resultado = self.controller.criar(objeto.id, objeto.id, "referência")

        self.assertFalse(resultado.sucesso)
        self.assertIn("auto-relação", resultado.mensagem_erro)

    def test_criar_com_destino_inexistente_retorna_erro_tratado(self) -> None:
        origem = self.objeto_service.cadastrar("Origem", "Nota")

        resultado = self.controller.criar(origem.id, 99999, "referência")

        self.assertFalse(resultado.sucesso)
        self.assertIn("origem ou destino", resultado.mensagem_erro)

    def test_criar_objeto_e_relacionar_cria_nota_e_relacao(self) -> None:
        origem = self.objeto_service.cadastrar("Origem", "Nota")

        resultado = self.controller.criar_objeto_e_relacionar(
            origem.id, "Nova nota", "complementa"
        )

        self.assertTrue(resultado.sucesso)
        nova_nota = self.objeto_service.obter_por_id(resultado.relacao.destino)
        self.assertEqual(nova_nota.titulo, "Nova nota")
        self.assertEqual(nova_nota.tipo, "Nota")
        self.assertEqual(
            self.relacao_service.listar_por_objeto(origem.id), [resultado.relacao]
        )

    def test_criar_objeto_e_relacionar_nao_cria_relacao_se_nota_falha(self) -> None:
        origem = self.objeto_service.cadastrar("Origem", "Nota")

        resultado = self.controller.criar_objeto_e_relacionar(
            origem.id, "", "complementa"
        )

        self.assertFalse(resultado.sucesso)
        self.assertIn("titulo", resultado.mensagem_erro.lower())
        self.assertEqual(self.relacao_service.listar_por_objeto(origem.id), [])


if __name__ == "__main__":
    unittest.main()
