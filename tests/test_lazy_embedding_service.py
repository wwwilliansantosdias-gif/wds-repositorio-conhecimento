"""Testes do facade de carregamento tardio do servico semantico."""

from __future__ import annotations

import sys
from unittest import TestCase
from unittest.mock import Mock, patch

PROJECT_ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from services.embedding_service import LazyEmbeddingService


class LazyEmbeddingServiceTests(TestCase):
    def test_consulta_nao_bloqueia_antes_da_carga(self) -> None:
        facade = LazyEmbeddingService(Mock())

        self.assertFalse(facade.disponivel)
        self.assertEqual(facade.buscar_semantico("termo"), [])
        self.assertEqual(facade.buscar_similares_a_objeto(1), [])

    @patch("services.embedding_service.EmbeddingService")
    def test_reproduz_indexacoes_enfileiradas_apos_carga(self, classe_servico) -> None:
        servico = classe_servico.return_value
        facade = LazyEmbeddingService(Mock())
        facade.indexar_objeto(1, "Titulo", None)
        facade.remover_do_indice(2)

        facade.carregar()

        servico.indexar_objeto.assert_called_once_with(1, "Titulo", None)
        servico.remover_do_indice.assert_called_once_with(2)
        self.assertTrue(facade.disponivel)

    @patch("services.embedding_service.EmbeddingService", side_effect=RuntimeError("falha"))
    def test_falha_fica_disponivel_para_indicador(self, _classe_servico) -> None:
        facade = LazyEmbeddingService(Mock())

        facade.carregar()

        self.assertFalse(facade.disponivel)
        self.assertIsInstance(facade.erro, RuntimeError)
