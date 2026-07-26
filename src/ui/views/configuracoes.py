"""View de Configurações.

Define o contêiner visual destinado às configurações do sistema. A
integração dos campos de configuração será realizada posteriormente.
"""

from __future__ import annotations

from typing import Any

import customtkinter as ctk


class ConfiguracoesView(ctk.CTkFrame):
    """Estrutura visual reservada para as Configurações."""

    def __init__(self, master: Any, **kwargs: Any) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Configurações\nAs opções do sistema serão exibidas aqui.",
            text_color="gray60",
            justify="center",
        ).grid(row=0, column=0)
