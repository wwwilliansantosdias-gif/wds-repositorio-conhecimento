"""Testes do cadastro, consulta e associação de tags."""

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
from services.tag_service import TagService


class TagServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        database = Database(Path(self.temporary_directory.name) / "banco.db")
        database.initialize()
        self.database = database
        self.service = TagService(database)
        self.objeto_service = ObjetoService(database)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_criar_persiste_tag(self) -> None:
        tag = self.service.criar("filosofia")

        self.assertEqual(tag.id, 1)
        self.assertEqual(tag.nome, "filosofia")

        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT nome FROM tabela_tags WHERE id = ?",
                (tag.id,),
            ).fetchone()

        self.assertEqual(dict(row), {"nome": "filosofia"})

    def test_criar_impede_tag_com_nome_duplicado(self) -> None:
        self.service.criar("filosofia")

        with self.assertRaisesRegex(ValueError, "tag já cadastrada: filosofia"):
            self.service.criar("filosofia")

    def test_listar_retorna_tags_em_ordem_de_nome(self) -> None:
        self.service.criar("zoologia")
        self.service.criar("arte")
        self.service.criar("biologia")

        tags = self.service.listar()

        self.assertEqual([tag.nome for tag in tags], ["arte", "biologia", "zoologia"])

    def test_associar_persiste_vinculo_entre_objeto_e_tag(self) -> None:
        objeto = self.objeto_service.cadastrar("Nota", "Pensamento")
        tag = self.service.criar("filosofia")

        self.service.associar(objeto.id, tag.id)

        with self.database.connection() as connection:
            row = connection.execute(
                """
                SELECT objeto_id, tag_id
                FROM tabela_objeto_tag
                WHERE objeto_id = ? AND tag_id = ?
                """,
                (objeto.id, tag.id),
            ).fetchone()

        self.assertEqual(dict(row), {"objeto_id": objeto.id, "tag_id": tag.id})

    def test_associar_objeto_inexistente_informa_erro_legivel(self) -> None:
        tag = self.service.criar("filosofia")

        with self.assertRaisesRegex(LookupError, "objeto ou tag não encontrado"):
            self.service.associar(999, tag.id)

    def test_associar_tag_inexistente_informa_erro_legivel(self) -> None:
        objeto = self.objeto_service.cadastrar("Nota", "Pensamento")

        with self.assertRaisesRegex(LookupError, "objeto ou tag não encontrado"):
            self.service.associar(objeto.id, 999)

    def test_desassociar_remove_vinculo_entre_objeto_e_tag(self) -> None:
        objeto = self.objeto_service.cadastrar("Nota", "Pensamento")
        tag = self.service.criar("filosofia")
        self.service.associar(objeto.id, tag.id)

        self.service.desassociar(objeto.id, tag.id)

        with self.database.connection() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM tabela_objeto_tag
                WHERE objeto_id = ? AND tag_id = ?
                """,
                (objeto.id, tag.id),
            ).fetchone()

        self.assertIsNone(row)

    def test_listar_por_objeto_retorna_apenas_tags_associadas(self) -> None:
        primeiro_objeto = self.objeto_service.cadastrar("Nota", "Pensamento")
        segundo_objeto = self.objeto_service.cadastrar("Artigo", "Texto")
        filosofia = self.service.criar("filosofia")
        arte = self.service.criar("arte")
        ciencia = self.service.criar("ciência")
        self.service.associar(primeiro_objeto.id, filosofia.id)
        self.service.associar(primeiro_objeto.id, arte.id)
        self.service.associar(segundo_objeto.id, ciencia.id)

        tags = self.service.listar_por_objeto(primeiro_objeto.id)

        self.assertEqual([tag.nome for tag in tags], ["arte", "filosofia"])


if __name__ == "__main__":
    unittest.main()
