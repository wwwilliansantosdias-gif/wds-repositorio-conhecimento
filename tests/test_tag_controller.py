"""Testes do TagController -- adicionar (obter-ou-criar) e remover tags."""

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
from services.objeto_service import ObjetoService
from services.tag_service import TagService

from controllers.tag_controller import TagController


class TagControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        temporary_path = Path(self.temporary_directory.name)

        self.database = Database(temporary_path / "banco.db")
        self.database.initialize()

        self.objeto_service = ObjetoService(self.database)
        self.tag_service = TagService(self.database)
        self.controller = TagController(self.tag_service, self.objeto_service)

    def tearDown(self) -> None:
        try:
            self.temporary_directory.cleanup()
        except PermissionError:
            pass

    def test_adicionar_tag_nova_cria_e_associa(self) -> None:
        objeto = self.objeto_service.cadastrar("Objeto 1", "Nota")

        resultado = self.controller.adicionar_tag(objeto.id, "filosofia")

        self.assertTrue(resultado.sucesso)
        self.assertEqual(resultado.tag.nome, "filosofia")

    def test_adicionar_tag_existente_reaproveita_em_vez_de_duplicar(self) -> None:
        objeto1 = self.objeto_service.cadastrar("Objeto 1", "Nota")
        objeto2 = self.objeto_service.cadastrar("Objeto 2", "Nota")

        r1 = self.controller.adicionar_tag(objeto1.id, "filosofia")
        r2 = self.controller.adicionar_tag(objeto2.id, "filosofia")

        self.assertEqual(r1.tag.id, r2.tag.id)
        self.assertEqual(len(self.controller.listar_todas()), 1)

    def test_adicionar_tag_com_nome_vazio_retorna_erro_tratado(self) -> None:
        objeto = self.objeto_service.cadastrar("Objeto 1", "Nota")

        resultado = self.controller.adicionar_tag(objeto.id, "   ")

        self.assertFalse(resultado.sucesso)
        self.assertIsNotNone(resultado.mensagem_erro)

    def test_adicionar_tag_a_objeto_inexistente_nao_cria_tag_orfa(self) -> None:
        """Regressao: a tag nao pode ser criada se a associacao ao
        objeto vai falhar, ja que TagService nao permite excluir uma
        tag depois -- isso deixaria uma tag orfa no sistema."""
        quantidade_antes = len(self.controller.listar_todas())

        resultado = self.controller.adicionar_tag(99999, "tag-orfa")

        self.assertFalse(resultado.sucesso)
        self.assertEqual(len(self.controller.listar_todas()), quantidade_antes)

    def test_listar_por_objeto_retorna_apenas_as_tags_daquele_objeto(self) -> None:
        objeto1 = self.objeto_service.cadastrar("Objeto 1", "Nota")
        objeto2 = self.objeto_service.cadastrar("Objeto 2", "Nota")
        self.controller.adicionar_tag(objeto1.id, "filosofia")
        self.controller.adicionar_tag(objeto2.id, "arte")

        tags_objeto1 = self.controller.listar_por_objeto(objeto1.id)

        self.assertEqual(len(tags_objeto1), 1)
        self.assertEqual(tags_objeto1[0].nome, "filosofia")

    def test_remover_tag_desassocia_sem_apagar_a_tag_em_si(self) -> None:
        objeto1 = self.objeto_service.cadastrar("Objeto 1", "Nota")
        objeto2 = self.objeto_service.cadastrar("Objeto 2", "Nota")
        resultado = self.controller.adicionar_tag(objeto1.id, "filosofia")
        self.controller.adicionar_tag(objeto2.id, "filosofia")

        self.controller.remover_tag(objeto1.id, resultado.tag.id)

        self.assertEqual(self.controller.listar_por_objeto(objeto1.id), [])
        self.assertEqual(len(self.controller.listar_todas()), 1)


if __name__ == "__main__":
    unittest.main()
