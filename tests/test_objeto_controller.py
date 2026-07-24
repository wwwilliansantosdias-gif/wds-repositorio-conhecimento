"""Testes do ObjetoController -- tela de Objeto em Foco e painel de Contexto."""

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

import chromadb

from persistence import Database
from services.acervo_service import AcervoService
from services.embedding_service import EmbeddingService
from services.objeto_service import ObjetoService
from services.relacao_service import RelacaoService
from services.tag_service import TagService

from controllers.objeto_controller import ObjetoController


class ObjetoControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        temporary_path = Path(self.temporary_directory.name)

        self.database = Database(temporary_path / "banco.db")
        self.database.initialize()

        self.objeto_service = ObjetoService(self.database)
        self.tag_service = TagService(self.database)
        self.relacao_service = RelacaoService(self.database)

        # EmbeddingService sem carregar o modelo real (evita rede nos testes).
        self.embedding_service = object.__new__(EmbeddingService)
        self.embedding_service._objeto_service = self.objeto_service
        client = chromadb.PersistentClient(
            path=str(temporary_path / "chroma_db")
        )
        self.embedding_service._collection = client.get_or_create_collection(
            name="objetos_conhecimento",
            metadata={"hnsw:space": "cosine"},
        )

        self.acervo_service = AcervoService(
            self.objeto_service, self.embedding_service
        )
        self.controller = ObjetoController(
            self.acervo_service,
            self.tag_service,
            self.relacao_service,
            self.embedding_service,
        )

    def tearDown(self) -> None:
        try:
            self.temporary_directory.cleanup()
        except PermissionError:
            pass

    def test_carregar_detalhe_retorna_o_objeto_correto(self) -> None:
        objeto = self.objeto_service.cadastrar("Objeto Alvo", "Nota")

        detalhe = self.controller.carregar_detalhe(objeto.id)

        self.assertEqual(detalhe.objeto.id, objeto.id)

    def test_carregar_detalhe_resolve_relacionamentos_explicitos_sem_score(
        self,
    ) -> None:
        alvo = self.objeto_service.cadastrar("Alvo", "Nota")
        relacionado = self.objeto_service.cadastrar("Relacionado", "Nota")
        self.relacao_service.criar(alvo.id, relacionado.id, "referencia")

        detalhe = self.controller.carregar_detalhe(alvo.id)

        self.assertEqual(len(detalhe.relacionamentos), 1)
        self.assertEqual(detalhe.relacionamentos[0].id, relacionado.id)

    def test_carregar_detalhe_resolve_relacao_em_qualquer_direcao(self) -> None:
        alvo = self.objeto_service.cadastrar("Alvo", "Nota")
        origem = self.objeto_service.cadastrar("Origem", "Nota")
        # alvo e o destino desta vez, nao a origem
        self.relacao_service.criar(origem.id, alvo.id, "complementa")

        detalhe = self.controller.carregar_detalhe(alvo.id)

        self.assertEqual(len(detalhe.relacionamentos), 1)
        self.assertEqual(detalhe.relacionamentos[0].id, origem.id)

    def test_carregar_detalhe_traz_sugestoes_semanticas_com_score(self) -> None:
        alvo = self.objeto_service.cadastrar("Alvo", "Nota")
        parecido = self.objeto_service.cadastrar("Parecido", "Nota")
        distante = self.objeto_service.cadastrar("Distante", "Nota")

        self.embedding_service._collection.upsert(
            ids=[str(alvo.id), str(parecido.id), str(distante.id)],
            embeddings=[[1.0, 0.0], [0.99, 0.01], [0.0, 1.0]],
        )

        detalhe = self.controller.carregar_detalhe(alvo.id)

        ids_sugeridos = [s.objeto.id for s in detalhe.sugestoes]
        self.assertNotIn(alvo.id, ids_sugeridos)
        self.assertIn(parecido.id, ids_sugeridos)
        sugestao_parecida = next(
            s for s in detalhe.sugestoes if s.objeto.id == parecido.id
        )
        self.assertIsInstance(sugestao_parecida.score, float)
        self.assertGreater(sugestao_parecida.score, 90)

    def test_carregar_detalhe_ignora_relacao_para_objeto_ja_removido(self) -> None:
        alvo = self.objeto_service.cadastrar("Alvo", "Nota")
        removido = self.objeto_service.cadastrar("Sera removido", "Nota")
        self.relacao_service.criar(alvo.id, removido.id, "referencia")

        self.objeto_service.excluir(removido.id)
        self.objeto_service.excluir_definitivamente(removido.id)

        # Nao deve levantar excecao, apenas omitir o objeto removido.
        detalhe = self.controller.carregar_detalhe(alvo.id)
        self.assertEqual(detalhe.relacionamentos, [])

    def test_carregar_detalhe_objeto_inexistente_lanca_lookup_error(self) -> None:
        with self.assertRaises(LookupError):
            self.controller.carregar_detalhe(99999)


if __name__ == "__main__":
    unittest.main()
