"""Ponto de entrada da aplicação WDS – Acervo de Conhecimento."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys

import customtkinter as ctk

SOURCE_DIRECTORY = Path(__file__).with_name("src")
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

THEME_PATH = SOURCE_DIRECTORY / "ui" / "themes" / "acervo.json"
ctk.set_default_color_theme(str(THEME_PATH))

from services.config_service import ConfigService
from ui.main_window import MainWindow

ctk.set_appearance_mode(ConfigService().carregar().tema_ctk)


def create_application() -> MainWindow:
    """Cria a janela principal que disponibiliza o MVP."""
    return MainWindow()


def main(arguments: Sequence[str] | None = None) -> int:
    """Inicia a aplicação ou valida sua inicialização sem abrir a janela."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="valida que a aplicação pode ser inicializada sem abrir a interface",
    )
    options = parser.parse_args(arguments)

    if options.check:
        return 0

    application = create_application()
    application.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
