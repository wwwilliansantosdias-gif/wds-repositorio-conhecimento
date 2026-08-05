"""Testes do painel de Objeto em Foco."""

from __future__ import annotations

from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import Mock, patch
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
UI_DIRECTORY = SOURCE_DIRECTORY / "ui"
for caminho in (SOURCE_DIRECTORY, UI_DIRECTORY):
    if str(caminho) not in sys.path:
        sys.path.insert(0, str(caminho))

from models import Objeto
from views.objeto_view import LIMITE_RESUMO_DETALHE, ObjetoView


class ObjetoViewTests(unittest.TestCase):
    def _criar_objeto(self, resumo: str | None) -> Objeto:
        return Objeto(
            id=1,
            titulo="Objeto de teste",
            tipo="PDF",
            caminho=r"C:\\acervo\\pdfs\\1.pdf",
            resumo=resumo,
            hash_arquivo=None,
            status="ativo",
            data_criacao="2026-08-01T10:00:00+00:00",
            data_edicao="2026-08-01T10:00:00+00:00",
            data_exclusao=None,
        )

    def _mostrar_objeto_e_capturar_labels(self, resumo: str) -> list[dict[str, object]]:
        objeto = self._criar_objeto(resumo)
        detalhe = SimpleNamespace(
            objeto=objeto,
            tags=[],
            relacionamentos=[],
            sugestoes=[],
        )
        view = object.__new__(ObjetoView)
        view._objeto_controller = Mock(carregar_detalhe=Mock(return_value=detalhe))
        view._renderizar_tags_e_entrada = Mock()
        view._renderizar_secao_contexto = Mock(side_effect=lambda linha, **kwargs: linha + 1)
        view.winfo_children = Mock(return_value=[])

        labels_criados: list[dict[str, object]] = []

        def criar_label(*args: object, **kwargs: object) -> Mock:
            labels_criados.append(kwargs)
            return Mock()

        with (
            patch("views.objeto_view.ctk.CTkFrame", return_value=Mock()),
            patch("views.objeto_view.ctk.CTkLabel", side_effect=criar_label),
            patch("views.objeto_view.ctk.CTkButton", return_value=Mock()),
            patch("views.objeto_view.ctk.CTkFont"),
        ):
            view.mostrar_objeto(1)

        return labels_criados

    def test_resumo_longo_e_truncado_no_painel_de_detalhe(self) -> None:
        resumo_longo = "x" * 5000
        labels = self._mostrar_objeto_e_capturar_labels(resumo_longo)

        textos_resumo = [
            kwargs["text"]
            for kwargs in labels
            if isinstance(kwargs.get("text"), str) and kwargs["text"].startswith("x")
        ]

        self.assertEqual(len(textos_resumo), 1)
        texto_resumo = textos_resumo[0]
        self.assertLessEqual(
            len(texto_resumo), LIMITE_RESUMO_DETALHE + len("... (truncado)")
        )
        self.assertTrue(texto_resumo.endswith("... (truncado)"))

    def test_resumo_curto_nao_e_truncado(self) -> None:
        resumo_curto = "Um resumo qualquer, bem curto."
        labels = self._mostrar_objeto_e_capturar_labels(resumo_curto)

        textos_resumo = [kwargs["text"] for kwargs in labels if kwargs.get("text") == resumo_curto]

        self.assertEqual(len(textos_resumo), 1)


if __name__ == "__main__":
    unittest.main()
