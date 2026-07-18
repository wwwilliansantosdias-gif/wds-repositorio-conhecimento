"""Ponto de entrada da aplicação WDS Repositório de Conhecimento."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys

import customtkinter as ctk


SOURCE_DIRECTORY = Path(__file__).with_name("src")
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from persistence.database import initialize_database


def create_application() -> ctk.CTk:
    """Cria a janela principal vazia da aplicação."""
    application = ctk.CTk()
    application.title("WDS Repositório de Conhecimento")
    return application


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

    initialize_database()
    application = create_application()
    application.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
