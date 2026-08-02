"""Testes do roteamento de importacao no menu Novo Objeto."""

from __future__ import annotations

from pathlib import Path
import sys
from unittest.mock import patch
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
UI_DIRECTORY = SOURCE_DIRECTORY / "ui"
for caminho in (SOURCE_DIRECTORY, UI_DIRECTORY):
    if str(caminho) not in sys.path:
        sys.path.insert(0, str(caminho))

from widgets.novo_objeto_menu import NovoObjetoMenu


class _ControllerStub:
    def __init__(self) -> None:
        self.caminho_recebido: str | None = None

    def importar_docx(self, caminho: str) -> None:
        self.caminho_recebido = caminho

    def importar_planilha(self, caminho: str) -> None:
        self.caminho_recebido = caminho

    def importar_pdf(self, caminho: str) -> None:
        pass

    def importar_markdown(self, caminho: str) -> None:
        pass


class NovoObjetoMenuTests(unittest.TestCase):
    def test_importar_arquivo_docx_rota_para_controller(self) -> None:
        caminho = r"C:\temp\documento.docx"
        controller = _ControllerStub()
        menu = object.__new__(NovoObjetoMenu)
        menu._controller = controller
        menu._executar = lambda chamada: chamada()

        with patch(
            "widgets.novo_objeto_menu.filedialog.askopenfilename",
            return_value=caminho,
        ):
            menu._importar_arquivo()

        self.assertEqual(controller.caminho_recebido, caminho)

    def test_importar_arquivo_xlsx_rota_para_controller(self) -> None:
        caminho = r"C:\temp\dados.xlsx"
        controller = _ControllerStub()
        menu = object.__new__(NovoObjetoMenu)
        menu._controller = controller
        menu._executar = lambda chamada: chamada()

        with patch(
            "widgets.novo_objeto_menu.filedialog.askopenfilename",
            return_value=caminho,
        ):
            menu._importar_arquivo()

        self.assertEqual(controller.caminho_recebido, caminho)


if __name__ == "__main__":
    unittest.main()
