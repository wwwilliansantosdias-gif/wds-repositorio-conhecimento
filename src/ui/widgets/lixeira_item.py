"""Widget de um item na tela de Lixeira.

Mostra o objeto e oferece duas acoes: Restaurar ou Excluir
Definitivamente. Diferente de ResultadoItem, nao e clicavel para
selecao -- as acoes sao sempre pelos botoes.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from models import Objeto


class LixeiraItem(ctk.CTkFrame):
    """Apresenta um objeto excluído e suas ações de recuperação."""

    def __init__(
        self,
        master: Any,
        objeto: Objeto,
        ao_restaurar: Callable[[int], None],
        ao_excluir_definitivamente: Callable[[int], None],
        **kwargs: Any,
    ) -> None:
        super().__init__(master, corner_radius=8, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text=objeto.titulo,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 0))

        ctk.CTkLabel(
            self,
            text=objeto.tipo,
            font=ctk.CTkFont(size=10),
            text_color="gray60",
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=12)

        botoes = ctk.CTkFrame(self, fg_color="transparent")
        botoes.grid(row=2, column=0, sticky="e", padx=12, pady=(6, 10))
        ctk.CTkButton(
            botoes,
            text="Restaurar",
            width=100,
            height=32,
            command=lambda: ao_restaurar(objeto.id),
        ).grid(row=0, column=0, padx=(0, 6))
        ctk.CTkButton(
            botoes,
            text="Excluir definitivamente",
            width=170,
            height=32,
            fg_color="#B33A3A",
            hover_color="#8F2E2E",
            command=lambda: ao_excluir_definitivamente(objeto.id),
        ).grid(row=0, column=1)
