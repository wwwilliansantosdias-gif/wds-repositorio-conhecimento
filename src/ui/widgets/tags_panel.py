"""Painel fixo com todas as tags do sistema.

Sempre visivel na janela principal (nao apenas dentro do objeto
selecionado), reaproveitando `TagController.listar_todas()`. Clicar
numa tag dispara a mesma busca textual ja usada pelo clique de tag
dentro de Objeto em Foco -- nao existe busca paralela para este
painel. Nunca oferece excluir ou desassociar uma tag: TagService nao
possui essa operacao (decisao ja registrada em tag_controller.py).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from controllers.tag_controller import TagController
from widgets.tag_chip import TagChip


class TagsPanel(ctk.CTkScrollableFrame):
    """Lista todas as tags do sistema para navegacao rapida."""

    def __init__(
        self,
        master: Any,
        tag_controller: TagController,
        ao_selecionar_tag: Callable[[str], None],
        **kwargs: Any,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._tag_controller = tag_controller
        self._ao_selecionar_tag = ao_selecionar_tag

        self.grid_columnconfigure(0, weight=1)

        self.atualizar()

    def atualizar(self) -> None:
        """Recarrega a lista de tags do zero."""
        for widget in self.winfo_children():
            widget.destroy()

        tags = self._tag_controller.listar_todas()

        if not tags:
            ctk.CTkLabel(
                self,
                text="Nenhuma tag cadastrada ainda.",
                text_color="gray60",
            ).grid(row=0, column=0, pady=40)
            return

        for indice, tag in enumerate(tags):
            chip = TagChip(self, tag, ao_selecionar=self._ao_selecionar_tag)
            chip.grid(row=indice, column=0, sticky="w", padx=8, pady=(0, 6))
