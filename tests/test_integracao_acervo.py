"""Teste de integração do fluxo de organização do acervo."""

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
from services.objeto_service import ObjetoService
from services.relacao_service import RelacaoService
from services.tag_service import TagService


class AcervoIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        database = Database(Path(self.temporary_directory.name) / "banco.db")
        database.initialize()
        self.objeto_service = ObjetoService(database)
        self.tag_service = TagService(database)
        self.relacao_service = RelacaoService(database)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_fluxo_de_organizacao_preserva_vinculos_na_lixeira(self) -> None:
        nota_a = self.objeto_service.cadastrar("Nota A", "Nota")
        nota_b = self.objeto_service.cadastrar("Nota B", "Nota")
        tag = self.tag_service.criar("estudo")
        self.tag_service.associar(nota_a.id, tag.id)
        relacao = self.relacao_service.criar(
            nota_a.id,
            nota_b.id,
            "referencia",
        )

        self.assertEqual(self.tag_service.listar_por_objeto(nota_a.id), [tag])
        self.assertEqual(self.relacao_service.listar_por_objeto(nota_a.id), [relacao])
        self.assertEqual(self.relacao_service.listar_por_objeto(nota_b.id), [relacao])

        self.objeto_service.excluir(nota_a.id)

        self.assertIn(tag, self.tag_service.listar())
        self.assertEqual(self.relacao_service.listar_por_objeto(nota_a.id), [relacao])
        self.assertEqual(self.relacao_service.listar_por_objeto(nota_b.id), [relacao])
        self.assertEqual(
            self.objeto_service.obter_por_id(nota_a.id).status,
            "lixeira",
        )


if __name__ == "__main__":
    unittest.main()
