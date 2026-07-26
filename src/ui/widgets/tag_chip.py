"""Widget de uma tag exibida como "chip" (pilula arredondada).

Pode ser somente leitura (usado na lista de Resultados) ou removivel
(usado no painel de Objeto em Foco, com um botao "x" ao lado).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from models import Tag


class TagChip(ctk.CTkFrame):
    """Exibe uma tag, opcionalmente com uma ação de remoção."""

    def __init__(
        self,
        master: Any,
        tag: Tag,
        ao_remover: Callable[[int], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master, corner_radius=12, fg_color=("#DCEEEC", "#1F3B38"), **kwargs
        )

        ctk.CTkLabel(
            self,
            text=f"#{tag.nome}",
            font=ctk.CTkFont(size=11),
            text_color="#4FA9A0",
        ).grid(row=0, column=0, padx=(8, 4 if ao_remover else 8), pady=2)

        if ao_remover is not None:
            ctk.CTkButton(
                self,
                text="x",
                width=16,
                height=16,
                fg_color="transparent",
                hover_color=("#C5E4E1", "#2A4D49"),
                text_color="#4FA9A0",
                font=ctk.CTkFont(size=10),
                command=lambda: ao_remover(tag.id),
            ).grid(row=0, column=1, padx=(0, 6), pady=2)
