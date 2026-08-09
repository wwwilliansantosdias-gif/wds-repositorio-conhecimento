"""Painel fixo com todas as tags do sistema.

Sempre visivel na janela principal (nao apenas dentro do objeto
selecionado), reaproveitando `TagController.listar_todas()`. Clicar
numa tag dispara a mesma busca textual ja usada pelo clique de tag
dentro de Objeto em Foco -- nao existe busca paralela para este
painel. Nunca oferece excluir ou desassociar uma tag: TagService nao
possui essa operacao (decisao ja registrada em tag_controller.py).

Tambem mostra, acima da lista, um contador de objetos ativos no
acervo (AcervoService.contar_ativos()) -- ponto de leitura rapido e
sempre visivel, sem precisar abrir a Biblioteca.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from controllers.tag_controller import TagController
from services.acervo_service import AcervoService
from widgets.tag_chip import TagChip


class TagsPanel(ctk.CTkScrollableFrame):
    """Lista todas as tags do sistema para navegacao rapida."""

    def __init__(
        self,
        master: Any,
        tag_controller: TagController,
        acervo_service: AcervoService,
        ao_selecionar_tag: Callable[[str], None],
        **kwargs: Any,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._tag_controller = tag_controller
        self._acervo_service = acervo_service
        self._ao_selecionar_tag = ao_selecionar_tag

        self.grid_columnconfigure(0, weight=1)

        self.atualizar()

    def atualizar(self) -> None:
        """Recarrega o contador de objetos e a lista de tags do zero."""
        for widget in self.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self,
            text=_texto_contador(self._acervo_service.contar_ativos()),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray60",
        ).grid(row=0, column=0, sticky="w", padx=8, pady=(0, 10))

        tags = self._tag_controller.listar_todas()

        if not tags:
            ctk.CTkLabel(
                self,
                text="Nenhuma tag cadastrada ainda.",
                text_color="gray60",
            ).grid(row=1, column=0, pady=40)
            return

        for indice, tag in enumerate(tags, start=1):
            chip = TagChip(self, tag, ao_selecionar=self._ao_selecionar_tag)
            chip.grid(row=indice, column=0, sticky="w", padx=8, pady=(0, 6))


def _texto_contador(total: int) -> str:
    """Formata o contador com singular/plural correto para 0 e 1."""
    sufixo = "objeto" if total == 1 else "objetos"
    return f"{total} {sufixo} no acervo"
