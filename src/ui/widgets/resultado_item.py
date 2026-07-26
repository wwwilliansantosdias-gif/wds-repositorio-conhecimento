"""Widget de um item na lista de resultados (Pesquisa/Biblioteca/Lixeira).

Mostra titulo, tipo, resumo curto, tags e, quando disponivel, o score
de similaridade semantica. Notifica um callback externo ao ser
selecionado -- nao decide sozinho o que acontece depois do clique.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from models import Objeto, Tag


class ResultadoItem(ctk.CTkFrame):
    """Apresenta um objeto recuperado em uma lista de resultados."""

    def __init__(
        self,
        master: Any,
        objeto: Objeto,
        tags: list[Tag],
        ao_selecionar: Callable[[int], None],
        score: float | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, corner_radius=8, **kwargs)
        self._objeto_id = objeto.id
        self._ao_selecionar = ao_selecionar

        self.grid_columnconfigure(0, weight=1)

        cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        cabecalho.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 0))
        cabecalho.grid_columnconfigure(0, weight=1)

        titulo_label = ctk.CTkLabel(
            cabecalho,
            text=objeto.titulo,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        titulo_label.grid(row=0, column=0, sticky="w")

        if score is not None:
            ctk.CTkLabel(
                cabecalho,
                text=f"{score:.0f}%",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#4FA9A0",
            ).grid(row=0, column=1, padx=(8, 0))

        ctk.CTkLabel(
            self,
            text=objeto.tipo,
            font=ctk.CTkFont(size=10),
            text_color="gray60",
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=12)

        if objeto.resumo:
            resumo_texto = objeto.resumo.strip().replace("\n", " ")
            if len(resumo_texto) > 140:
                resumo_texto = resumo_texto[:140].rstrip() + "..."
            ctk.CTkLabel(
                self,
                text=resumo_texto,
                font=ctk.CTkFont(size=12),
                anchor="w",
                justify="left",
                wraplength=360,
            ).grid(row=2, column=0, sticky="w", padx=12, pady=(4, 0))

        if tags:
            tags_texto = "  ".join(f"#{tag.nome}" for tag in tags)
            ctk.CTkLabel(
                self,
                text=tags_texto,
                font=ctk.CTkFont(size=11),
                text_color="#5AADA3",
                anchor="w",
            ).grid(row=3, column=0, sticky="w", padx=12, pady=(4, 10))
        else:
            ctk.CTkLabel(self, text="", height=1).grid(row=3, column=0, pady=(0, 10))

        for widget in (self, cabecalho, titulo_label):
            widget.bind("<Button-1>", self._selecionar)

    def _selecionar(self, _evento: object | None = None) -> None:
        self._ao_selecionar(self._objeto_id)
