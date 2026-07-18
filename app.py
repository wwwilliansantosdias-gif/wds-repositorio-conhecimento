"""Ponto de entrada da aplicação WDS Repositório de Conhecimento."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

import customtkinter as ctk


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

    application = create_application()
    application.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
