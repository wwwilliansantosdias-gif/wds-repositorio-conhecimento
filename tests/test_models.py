"""Testes dos modelos de domínio."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from models import Objeto, Relacao, Tag


class ObjetoTests(unittest.TestCase):
    def test_representa_todos_os_campos_do_schema(self) -> None:
        objeto = Objeto(
            id=1,
            titulo="Nota de teste",
            tipo="Pensamento",
            caminho=None,
            resumo=None,
            hash_arquivo=None,
            status="ativo",
            data_criacao="2026-07-18T10:00:00+00:00",
            data_edicao="2026-07-18T10:00:00+00:00",
            data_exclusao=None,
        )

        self.assertEqual(objeto.id, 1)
        self.assertEqual(objeto.titulo, "Nota de teste")
        self.assertEqual(objeto.tipo, "Pensamento")
        self.assertIsNone(objeto.caminho)
        self.assertIsNone(objeto.resumo)
        self.assertIsNone(objeto.hash_arquivo)
        self.assertEqual(objeto.status, "ativo")
        self.assertEqual(objeto.data_criacao, "2026-07-18T10:00:00+00:00")
        self.assertEqual(objeto.data_edicao, "2026-07-18T10:00:00+00:00")
        self.assertIsNone(objeto.data_exclusao)

    def test_aceita_status_ativo_e_lixeira(self) -> None:
        base = {
            "id": 1,
            "titulo": "Nota",
            "tipo": "Pensamento",
            "caminho": None,
            "resumo": None,
            "hash_arquivo": None,
            "data_criacao": "2026-07-18T10:00:00+00:00",
            "data_edicao": "2026-07-18T10:00:00+00:00",
            "data_exclusao": None,
        }

        self.assertEqual(Objeto(status="ativo", **base).status, "ativo")
        self.assertEqual(Objeto(status="lixeira", **base).status, "lixeira")

    def test_rejeita_status_nao_documentado(self) -> None:
        with self.assertRaisesRegex(ValueError, "status deve ser"):
            Objeto(
                id=1,
                titulo="Nota",
                tipo="Pensamento",
                caminho=None,
                resumo=None,
                hash_arquivo=None,
                status="arquivado",
                data_criacao="2026-07-18T10:00:00+00:00",
                data_edicao="2026-07-18T10:00:00+00:00",
                data_exclusao=None,
            )


class TagTests(unittest.TestCase):
    def test_representa_campos_da_tabela_tags(self) -> None:
        tag = Tag(id=1, nome="filosofia")

        self.assertEqual(tag.id, 1)
        self.assertEqual(tag.nome, "filosofia")


class RelacaoTests(unittest.TestCase):
    def test_representa_campos_da_tabela_relacoes(self) -> None:
        relacao = Relacao(origem=1, destino=2, tipo_relacao="referencia")

        self.assertEqual(relacao.origem, 1)
        self.assertEqual(relacao.destino, 2)
        self.assertEqual(relacao.tipo_relacao, "referencia")
