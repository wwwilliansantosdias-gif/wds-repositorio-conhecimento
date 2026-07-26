"""View do Editor Markdown.

Define o contêiner visual destinado à futura edição de notas Markdown.
As operações de carregar e salvar permanecem sob responsabilidade do
``EditorMarkdownController`` quando esta tela for integrada.
"""

from __future__ import annotations

from typing import Any

import customtkinter as ctk


class EditorMarkdownView(ctk.CTkFrame):
    """Estrutura visual reservada para o Editor Markdown."""

    def __init__(self, master: Any, **kwargs: Any) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Editor Markdown\nA edição de notas será disponibilizada aqui.",
            text_color="gray60",
            justify="center",
        ).grid(row=0, column=0)
