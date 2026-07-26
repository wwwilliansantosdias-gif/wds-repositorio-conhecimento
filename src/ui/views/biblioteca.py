"""View da Biblioteca.

Define o contêiner visual destinado à apresentação dos Objetos de
Conhecimento. A listagem será integrada em incremento posterior.
"""

from __future__ import annotations

from typing import Any

import customtkinter as ctk


class BibliotecaView(ctk.CTkFrame):
    """Estrutura visual reservada para a Biblioteca."""

    def __init__(self, master: Any, **kwargs: Any) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Biblioteca\nOs Objetos de Conhecimento serão exibidos aqui.",
            text_color="gray60",
            justify="center",
        ).grid(row=0, column=0)
