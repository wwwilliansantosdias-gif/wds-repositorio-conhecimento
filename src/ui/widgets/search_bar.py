"""Widget da barra de pesquisa (search_bar).

Campo de texto + acionamento por Enter ou pelo botao, notificando um
callback externo com o termo digitado. Nao conhece PesquisaController
nem nenhum Service -- apenas coleta o termo e avisa quem o criou.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import customtkinter as ctk


class SearchBar(ctk.CTkFrame):
    """Campo de busca reutilizavel.

    Uso:
        barra = SearchBar(pai, ao_pesquisar=lambda termo: ...)
    """

    def __init__(
        self,
        master: Any,
        ao_pesquisar: Callable[[str], None],
        placeholder: str = "Pesquisar no Acervo...",
        **kwargs: Any,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._ao_pesquisar = ao_pesquisar

        self.grid_columnconfigure(0, weight=1)

        self._campo = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            height=36,
        )
        self._campo.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._campo.bind("<Return>", self._disparar_pesquisa)

        self._botao = ctk.CTkButton(
            self,
            text="Buscar",
            width=80,
            height=36,
            command=self._disparar_pesquisa,
        )
        self._botao.grid(row=0, column=1)

    def _disparar_pesquisa(self, _evento: object | None = None) -> None:
        termo = self._campo.get()
        self._ao_pesquisar(termo)

    def obter_termo(self) -> str:
        """Retorna o termo atualmente digitado no campo de busca."""
        return self._campo.get()

    def focar(self) -> None:
        """Posiciona o foco do teclado no campo de busca."""
        self._campo.focus_set()
