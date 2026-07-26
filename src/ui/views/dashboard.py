"""View do Dashboard.

Define o contêiner visual da tela inicial do WDS. Os acessos rápidos
serão incorporados em um incremento posterior da interface.
"""

from __future__ import annotations

from typing import Any

import customtkinter as ctk


class DashboardView(ctk.CTkFrame):
    """Estrutura visual reservada para o Dashboard."""

    def __init__(self, master: Any, **kwargs: Any) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Dashboard\nOs acessos rápidos serão exibidos aqui.",
            text_color="gray60",
            justify="center",
        ).grid(row=0, column=0)
