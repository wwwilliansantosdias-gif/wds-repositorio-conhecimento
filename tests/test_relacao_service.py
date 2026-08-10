"""Testes da criação, remoção e consulta de relações."""

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
from models import Relacao
from services.objeto_service import ObjetoService
from services.relacao_service import RelacaoService


class RelacaoServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        database = Database(Path(self.temporary_directory.name) / "banco.db")
        database.initialize()
        self.database = database
        self.service = RelacaoService(database)
        self.objeto_service = ObjetoService(database)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_criar_persiste_relacao(self) -> None:
        origem = self.objeto_service.cadastrar("Nota", "Pensamento")
        destino = self.objeto_service.cadastrar("Artigo", "Texto")

        relacao = self.service.criar(origem.id, destino.id, "referencia")

        self.assertEqual(relacao.origem, origem.id)
        self.assertEqual(relacao.destino, destino.id)
        self.assertEqual(relacao.tipo_relacao, "referencia")
        with self.database.connection() as connection:
            row = connection.execute(
                """
                SELECT origem, destino, tipo_relacao
                FROM tabela_relacoes
                """
            ).fetchone()

        self.assertEqual(dict(row), {
            "origem": origem.id,
            "destino": destino.id,
            "tipo_relacao": "referencia",
        })

    def test_criar_informa_erro_legivel_para_origem_inexistente(self) -> None:
        destino = self.objeto_service.cadastrar("Artigo", "Texto")

        with self.assertRaisesRegex(LookupError, "origem ou destino não encontrado"):
            self.service.criar(999, destino.id, "referencia")

    def test_criar_informa_erro_legivel_para_destino_inexistente(self) -> None:
        origem = self.objeto_service.cadastrar("Nota", "Pensamento")

        with self.assertRaisesRegex(LookupError, "origem ou destino não encontrado"):
            self.service.criar(origem.id, 999, "referencia")

    def test_criar_rejeita_auto_relacao_antes_de_consultar_o_banco(self) -> None:
        with self.assertRaisesRegex(ValueError, "auto-relação não é permitida"):
            self.service.criar(999, 999, "referencia")

    def test_criar_relacao_duplicada_retorna_erro_tratado(self) -> None:
        origem = self.objeto_service.cadastrar("Nota", "Pensamento")
        destino = self.objeto_service.cadastrar("Artigo", "Texto")
        self.service.criar(origem.id, destino.id, "referencia")

        with self.assertRaisesRegex(ValueError, "existe"):
            self.service.criar(origem.id, destino.id, "referencia")

    def test_listar_tipos_distintos_retorna_lista_vazia_sem_relacoes(self) -> None:
        self.assertEqual(self.service.listar_tipos_distintos(), [])

    def test_listar_tipos_distintos_remove_repetidos_e_ordena(self) -> None:
        primeiro = self.objeto_service.cadastrar("Primeiro", "Nota")
        segundo = self.objeto_service.cadastrar("Segundo", "Nota")
        terceiro = self.objeto_service.cadastrar("Terceiro", "Nota")
        self.service.criar(primeiro.id, segundo.id, "zeta")
        self.service.criar(primeiro.id, terceiro.id, "alfa")
        self.service.criar(segundo.id, terceiro.id, "zeta")

        self.assertEqual(self.service.listar_tipos_distintos(), ["alfa", "zeta"])

    def test_remover_exclui_apenas_a_relacao_informada(self) -> None:
        origem = self.objeto_service.cadastrar("Nota", "Pensamento")
        destino = self.objeto_service.cadastrar("Artigo", "Texto")
        outro_destino = self.objeto_service.cadastrar("Livro", "Referência")
        self.service.criar(origem.id, destino.id, "referencia")
        self.service.criar(origem.id, outro_destino.id, "referencia")

        self.service.remover(origem.id, destino.id, "referencia")

        self.assertEqual(
            self.service.listar_por_objeto(origem.id),
            [Relacao(origem.id, outro_destino.id, "referencia")],
        )

    def test_listar_por_objeto_retorna_relacoes_como_origem_ou_destino(self) -> None:
        primeiro = self.objeto_service.cadastrar("Primeiro", "Nota")
        segundo = self.objeto_service.cadastrar("Segundo", "Nota")
        terceiro = self.objeto_service.cadastrar("Terceiro", "Nota")
        quarto = self.objeto_service.cadastrar("Quarto", "Nota")
        self.service.criar(primeiro.id, segundo.id, "referencia")
        self.service.criar(terceiro.id, primeiro.id, "complementa")
        self.service.criar(segundo.id, quarto.id, "referencia")

        relacoes = self.service.listar_por_objeto(primeiro.id)

        self.assertEqual(
            [(relacao.origem, relacao.destino, relacao.tipo_relacao) for relacao in relacoes],
            [
                (primeiro.id, segundo.id, "referencia"),
                (terceiro.id, primeiro.id, "complementa"),
            ],
        )

if __name__ == "__main__":
    unittest.main()
