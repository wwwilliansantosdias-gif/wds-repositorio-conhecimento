"""Testes dos ativos e valores da identidade visual do Acervo."""

from __future__ import annotations

import json
from pathlib import Path
import struct
import unittest
from unittest.mock import Mock, patch
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
THEME_PATH = PROJECT_ROOT / "src" / "ui" / "themes" / "acervo.json"
ICON_PATH = PROJECT_ROOT / "src" / "ui" / "assets" / "acervo.ico"
SOURCE_DIRECTORY = PROJECT_ROOT / "src" / "ui"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from widgets.toolbar import Toolbar


class IdentidadeVisualTests(unittest.TestCase):
    @staticmethod
    def _contraste(cor_frente: str, cor_fundo: str) -> float:
        def luminancia(cor: str) -> float:
            canais = [int(cor[pos : pos + 2], 16) / 255 for pos in (1, 3, 5)]
            lineares = [
                canal / 12.92
                if canal <= 0.04045
                else ((canal + 0.055) / 1.055) ** 2.4
                for canal in canais
            ]
            return 0.2126 * lineares[0] + 0.7152 * lineares[1] + 0.0722 * lineares[2]

        primeira, segunda = luminancia(cor_frente), luminancia(cor_fundo)
        clara, escura = max(primeira, segunda), min(primeira, segunda)
        return (clara + 0.05) / (escura + 0.05)

    def test_tema_mantem_cores_padrao_e_define_destaque_do_acervo(self) -> None:
        tema = json.loads(THEME_PATH.read_text(encoding="utf-8"))

        self.assertEqual(tema["CTkButton"]["fg_color"], ["#3B8ED0", "#1F6AA5"])
        self.assertEqual(tema["WDS"]["accent_fg_color"], ["#1F6E64", "#155048"])
        self.assertEqual(tema["WDS"]["accent_hover_color"], ["#2C8478", "#1D6156"])
        self.assertEqual(tema["WDS"]["accent_text_color"], ["#F1FAF7", "#F1FAF7"])

    def test_texto_tem_contraste_aa_sobre_o_destaque_nos_dois_modos(self) -> None:
        tema = json.loads(THEME_PATH.read_text(encoding="utf-8"))["WDS"]

        for cor_destaque in tema["accent_fg_color"]:
            with self.subTest(cor_destaque=cor_destaque):
                self.assertGreaterEqual(
                    self._contraste(tema["accent_text_color"][0], cor_destaque),
                    4.5,
                )

    def test_icone_do_acervo_e_um_arquivo_ico_valido(self) -> None:
        cabecalho = ICON_PATH.read_bytes()[:6]
        reservado, tipo, quantidade = struct.unpack("<HHH", cabecalho)

        self.assertEqual(reservado, 0)
        self.assertEqual(tipo, 1)
        self.assertGreaterEqual(quantidade, 1)

    def test_item_de_navegacao_acionado_recebe_o_destaque(self) -> None:
        toolbar = Toolbar.__new__(Toolbar)
        biblioteca = Mock()
        lixeira = Mock()
        toolbar._botoes_navegacao = {
            "biblioteca": biblioteca,
            "lixeira": lixeira,
        }
        acao = Mock()

        with patch(
            "widgets.toolbar._acervo_theme_color", side_effect=lambda nome: nome
        ):
            toolbar._acionar_navegacao("biblioteca", acao)

        biblioteca.configure.assert_called_once_with(
            fg_color="accent_fg_color",
            hover_color="accent_hover_color",
            text_color="accent_text_color",
        )
        lixeira.configure.assert_called_once_with(
            fg_color="gray40", hover_color="gray30"
        )
        acao.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
