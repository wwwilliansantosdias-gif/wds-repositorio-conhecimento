"""Testes do LixeiraController -- listar, restaurar e excluir definitivamente."""

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
from services.objeto_service import ObjetoService

from controllers.lixeira_controller import LixeiraController


class EmbeddingServiceStub:
    """Substituto do EmbeddingService, evitando depender de rede nestes
    testes, que validam apenas a logica da Lixeira."""

    def indexar_objeto(self, *args, **kwargs) -> None:
        pass

    def remover_do_indice(self, *args, **kwargs) -> None:
        pass


class LixeiraControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        temporary_path = Path(self.temporary_directory.name)

        self.database = Database(temporary_path / "banco.db")
        self.database.initialize()

        self.objeto_service = ObjetoService(self.database)
        self.acervo_service = AcervoService(
            self.objeto_service, EmbeddingServiceStub()
        )
        self.controller = LixeiraController(self.acervo_service)

    def tearDown(self) -> None:
        try:
            self.temporary_directory.cleanup()
        except PermissionError:
            pass

    def test_listar_comeca_vazia(self) -> None:
        self.assertEqual(self.controller.listar(), [])

    def test_objeto_excluido_aparece_na_lixeira(self) -> None:
        objeto = self.acervo_service.cadastrar("Nota A", "Nota")
        self.acervo_service.excluir(objeto.id)

        lixeira = self.controller.listar()

        self.assertEqual(len(lixeira), 1)
        self.assertEqual(lixeira[0].id, objeto.id)

    def test_restaurar_com_sucesso_remove_da_lixeira(self) -> None:
        objeto = self.acervo_service.cadastrar("Nota A", "Nota")
        self.acervo_service.excluir(objeto.id)

        resultado = self.controller.restaurar(objeto.id)

        self.assertTrue(resultado.sucesso)
        self.assertEqual(resultado.objeto.status, "ativo")
        self.assertEqual(self.controller.listar(), [])

    def test_restaurar_objeto_inexistente_retorna_erro_tratado(self) -> None:
        resultado = self.controller.restaurar(99999)

        self.assertFalse(resultado.sucesso)
        self.assertIsNotNone(resultado.mensagem_erro)

    def test_excluir_definitivamente_objeto_ativo_retorna_erro_tratado(self) -> None:
        objeto = self.acervo_service.cadastrar("Nota A", "Nota")

        resultado = self.controller.excluir_definitivamente(objeto.id)

        self.assertFalse(resultado.sucesso)
        self.assertIsNotNone(resultado.mensagem_erro)

    def test_excluir_definitivamente_com_sucesso_remove_o_objeto(self) -> None:
        objeto = self.acervo_service.cadastrar("Nota A", "Nota")
        self.acervo_service.excluir(objeto.id)

        resultado = self.controller.excluir_definitivamente(objeto.id)

        self.assertTrue(resultado.sucesso)
        with self.assertRaises(LookupError):
            self.acervo_service.obter_por_id(objeto.id)

    def test_excluir_definitivamente_objeto_inexistente_retorna_erro_tratado(
        self,
    ) -> None:
        resultado = self.controller.excluir_definitivamente(99999)

        self.assertFalse(resultado.sucesso)
        self.assertIsNotNone(resultado.mensagem_erro)


if __name__ == "__main__":
    unittest.main()
