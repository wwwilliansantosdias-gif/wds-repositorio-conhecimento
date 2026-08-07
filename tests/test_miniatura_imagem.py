"""Testes da miniatura de imagem no painel de Objeto em Foco."""

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

from PIL import Image

from widgets.miniatura_imagem import TAMANHO_MAXIMO, carregar_miniatura


class CarregarMiniaturaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.temporary_path = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        try:
            self.temporary_directory.cleanup()
        except PermissionError:
            pass

    def test_carrega_e_redimensiona_imagem_grande_preservando_proporcao(self) -> None:
        caminho = self.temporary_path / "grande.png"
        Image.new("RGB", (2000, 1000), color="blue").save(caminho)

        miniatura = carregar_miniatura(str(caminho))

        self.assertIsNotNone(miniatura)
        self.assertLessEqual(miniatura.width, TAMANHO_MAXIMO[0])
        self.assertLessEqual(miniatura.height, TAMANHO_MAXIMO[1])
        self.assertAlmostEqual(miniatura.width / miniatura.height, 2000 / 1000, places=2)

    def test_nao_amplia_imagem_menor_que_o_tamanho_maximo(self) -> None:
        caminho = self.temporary_path / "pequena.png"
        Image.new("RGB", (50, 30), color="green").save(caminho)

        miniatura = carregar_miniatura(str(caminho))

        self.assertEqual(miniatura.size, (50, 30))

    def test_caminho_none_retorna_none(self) -> None:
        self.assertIsNone(carregar_miniatura(None))

    def test_arquivo_inexistente_retorna_none(self) -> None:
        caminho_inexistente = str(self.temporary_path / "nao-existe.png")

        self.assertIsNone(carregar_miniatura(caminho_inexistente))

    def test_arquivo_corrompido_retorna_none_sem_levantar_excecao(self) -> None:
        caminho = self.temporary_path / "corrompido.png"
        caminho.write_bytes(b"isto nao e uma imagem valida")

        self.assertIsNone(carregar_miniatura(str(caminho)))


if __name__ == "__main__":
    unittest.main()
