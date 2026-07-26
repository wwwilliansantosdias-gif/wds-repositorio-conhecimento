"""Widget da Barra Superior.

Contem a identificacao do WDS, o campo de pesquisa (sempre visivel,
ancora da navegacao), o botao Novo Objeto e o acesso a Lixeira,
conforme docs/interface-grafica.md.

Decisao (nao especificada anteriormente, resolvida aqui): o acesso a
Lixeira e um pequeno botao na Barra Superior, ja que ela abre como
janela separada e nao substitui o conteudo principal.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from widgets.search_bar import SearchBar


class Toolbar(ctk.CTkFrame):
    """Compõe a barra superior de navegação do WDS."""

    def __init__(
        self,
        master: Any,
        ao_pesquisar: Callable[[str], None],
        ao_clicar_novo_objeto: Callable[[int, int], None],
        ao_clicar_lixeira: Callable[[], None],
        **kwargs: Any,
    ) -> None:
        super().__init__(master, corner_radius=0, **kwargs)

        self.grid_columnconfigure(1, weight=1)

        titulo = ctk.CTkLabel(
            self,
            text="WDS",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        titulo.grid(row=0, column=0, padx=(16, 24), pady=12)

        self.search_bar = SearchBar(self, ao_pesquisar=ao_pesquisar)
        self.search_bar.grid(row=0, column=1, sticky="ew", pady=12)

        self.botao_lixeira = ctk.CTkButton(
            self,
            text="Lixeira",
            width=90,
            height=36,
            fg_color="gray40",
            hover_color="gray30",
            command=ao_clicar_lixeira,
        )
        self.botao_lixeira.grid(row=0, column=2, padx=(16, 8), pady=12)

        self.botao_novo_objeto = ctk.CTkButton(
            self,
            text="+ Novo Objeto",
            width=140,
            height=36,
        )
        self.botao_novo_objeto.grid(row=0, column=3, padx=(0, 16), pady=12)
        self.botao_novo_objeto.bind(
            "<Button-1>",
            lambda evento: ao_clicar_novo_objeto(evento.x_root, evento.y_root),
        )
