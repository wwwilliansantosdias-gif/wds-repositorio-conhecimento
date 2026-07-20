"""Testes do cadastro, atualização e consulta de objetos."""

from __future__ import annotations

from datetime import datetime
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


class ObjetoServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        database = Database(Path(self.temporary_directory.name) / "banco.db")
        database.initialize()
        self.database = database
        self.service = ObjetoService(database)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_cadastrar_persiste_todos_os_metadados_do_objeto(self) -> None:
        objeto = self.service.cadastrar(
            "Ideia sobre leitura",
            "Pensamento",
            caminho="acervo/notas/1.md",
            resumo="Um resumo",
            hash_arquivo="abc123",
        )

        self.assertEqual(objeto.id, 1)
        self.assertEqual(objeto.titulo, "Ideia sobre leitura")
        self.assertEqual(objeto.tipo, "Pensamento")
        self.assertEqual(objeto.caminho, "acervo/notas/1.md")
        self.assertEqual(objeto.resumo, "Um resumo")
        self.assertEqual(objeto.hash_arquivo, "abc123")
        self.assertEqual(objeto.status, "ativo")
        self.assertIsNone(objeto.data_exclusao)
        self.assertEqual(objeto.data_criacao, objeto.data_edicao)
        self.assertIsNotNone(datetime.fromisoformat(objeto.data_criacao))

        with self.database.connection() as connection:
            row = connection.execute(
                """
                SELECT titulo, tipo, caminho, resumo, hash_arquivo, status
                FROM tabela_objetos
                WHERE id = ?
                """,
                (objeto.id,),
            ).fetchone()

        self.assertEqual(
            dict(row),
            {
                "titulo": "Ideia sobre leitura",
                "tipo": "Pensamento",
                "caminho": "acervo/notas/1.md",
                "resumo": "Um resumo",
                "hash_arquivo": "abc123",
                "status": "ativo",
            },
        )

    def test_atualizar_mantem_campos_opcionais_omitidos(self) -> None:
        cadastrado = self.service.cadastrar(
            "Rascunho",
            "Pensamento",
            caminho="acervo/notas/1.md",
            resumo="Versão inicial",
            hash_arquivo="abc123",
        )

        atualizado = self.service.atualizar(
            cadastrado.id,
            "Nota revisada",
            "Artigo",
        )

        self.assertEqual(atualizado.id, cadastrado.id)
        self.assertEqual(atualizado.titulo, "Nota revisada")
        self.assertEqual(atualizado.tipo, "Artigo")
        self.assertEqual(atualizado.caminho, "acervo/notas/1.md")
        self.assertEqual(atualizado.resumo, "Versão inicial")
        self.assertEqual(atualizado.hash_arquivo, "abc123")
        self.assertEqual(atualizado.status, "ativo")
        self.assertEqual(atualizado.data_criacao, cadastrado.data_criacao)
        self.assertIsNone(atualizado.data_exclusao)
        self.assertGreaterEqual(
            datetime.fromisoformat(atualizado.data_edicao),
            datetime.fromisoformat(cadastrado.data_edicao),
        )

    def test_atualizar_campos_opcionais_informados_substitui_valores(self) -> None:
        cadastrado = self.service.cadastrar(
            "Rascunho",
            "Pensamento",
            caminho="acervo/notas/1.md",
            resumo="Versão inicial",
            hash_arquivo="abc123",
        )

        atualizado = self.service.atualizar(
            cadastrado.id,
            "Nota revisada",
            "Artigo",
            caminho="acervo/notas/2.md",
            resumo="Versão revisada",
            hash_arquivo="def456",
        )

        self.assertEqual(atualizado.caminho, "acervo/notas/2.md")
        self.assertEqual(atualizado.resumo, "Versão revisada")
        self.assertEqual(atualizado.hash_arquivo, "def456")

    def test_atualizar_campos_opcionais_com_none_grava_null(self) -> None:
        cadastrado = self.service.cadastrar(
            "Rascunho",
            "Pensamento",
            caminho="acervo/notas/1.md",
            resumo="Versão inicial",
            hash_arquivo="abc123",
        )

        atualizado = self.service.atualizar(
            cadastrado.id,
            "Rascunho",
            "Pensamento",
            caminho=None,
            resumo=None,
            hash_arquivo=None,
        )

        self.assertIsNone(atualizado.caminho)
        self.assertIsNone(atualizado.resumo)
        self.assertIsNone(atualizado.hash_arquivo)

    def test_atualizar_objeto_inexistente_informa_ausencia_do_registro(self) -> None:
        with self.assertRaisesRegex(
            LookupError,
            "objeto não encontrado: 999",
        ):
            self.service.atualizar(
                999,
                "Inexistente",
                "Pensamento",
            )

    def test_obter_por_id_retorna_objeto_existente(self) -> None:
        cadastrado = self.service.cadastrar(
            "Livro",
            "Referência",
            caminho="acervo/livros/livro.pdf",
            resumo="Livro de exemplo",
            hash_arquivo="xyz789",
        )

        objeto = self.service.obter_por_id(cadastrado.id)

        self.assertEqual(objeto.id, cadastrado.id)
        self.assertEqual(objeto.titulo, "Livro")
        self.assertEqual(objeto.tipo, "Referência")
        self.assertEqual(objeto.caminho, "acervo/livros/livro.pdf")
        self.assertEqual(objeto.resumo, "Livro de exemplo")
        self.assertEqual(objeto.hash_arquivo, "xyz789")
        self.assertEqual(objeto.status, "ativo")

    def test_obter_por_id_objeto_inexistente_informa_ausencia_do_registro(self) -> None:
        with self.assertRaisesRegex(
            LookupError,
            "objeto não encontrado: 999",
        ):
            self.service.obter_por_id(999)

    def test_listar_sem_objetos_retorna_lista_vazia(self) -> None:
        objetos = self.service.listar()

        self.assertEqual(objetos, [])

    def test_listar_retorna_objetos_em_ordem_de_id(self) -> None:
        primeiro = self.service.cadastrar(
            "Primeiro",
            "Nota",
        )
        segundo = self.service.cadastrar(
            "Segundo",
            "Artigo",
        )
        terceiro = self.service.cadastrar(
            "Terceiro",
            "Livro",
        )

        objetos = self.service.listar()

        self.assertEqual(len(objetos), 3)
        self.assertEqual(
            [objeto.id for objeto in objetos],
            [primeiro.id, segundo.id, terceiro.id],
        )
        self.assertEqual(
            [objeto.titulo for objeto in objetos],
            ["Primeiro", "Segundo", "Terceiro"],
        )
        self.assertEqual(
            [objeto.tipo for objeto in objetos],
            ["Nota", "Artigo", "Livro"],
        )


if __name__ == "__main__":
    unittest.main()