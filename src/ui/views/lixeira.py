"""Janela da Lixeira -- tela propria incluida no MVP
(docs/interface-grafica.md).

Lista objetos excluidos logicamente e permite restaura-los ou
exclui-los definitivamente, delegando toda a logica ao
LixeiraController. Abre como janela separada (modal), sem substituir a
janela principal -- ao fechar, o usuario volta exatamente para onde
estava.
"""

from __future__ import annotations

from tkinter import messagebox
from typing import Any

import customtkinter as ctk

from controllers.lixeira_controller import LixeiraController
from widgets.lixeira_item import LixeiraItem


class LixeiraWindow(ctk.CTkToplevel):
    """Janela modal para as ações disponíveis na Lixeira."""

    def __init__(
        self,
        master: Any,
        lixeira_controller: LixeiraController,
    ) -> None:
        super().__init__(master)
        self.title("Lixeira")
        self.geometry("520x600")
        self._controller = lixeira_controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._lista_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._lista_scroll.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self._lista_scroll.grid_columnconfigure(0, weight=1)

        self._atualizar_lista()

    def _atualizar_lista(self) -> None:
        for widget in self._lista_scroll.winfo_children():
            widget.destroy()

        objetos = self._controller.listar()

        if not objetos:
            ctk.CTkLabel(
                self._lista_scroll,
                text="A lixeira esta vazia.",
                text_color="gray60",
            ).grid(row=0, column=0, pady=40)
            return

        for indice, objeto in enumerate(objetos):
            item = LixeiraItem(
                self._lista_scroll,
                objeto=objeto,
                ao_restaurar=self._restaurar,
                ao_excluir_definitivamente=self._excluir_definitivamente,
            )
            item.grid(row=indice, column=0, sticky="ew", pady=(0, 8))

    def _restaurar(self, objeto_id: int) -> None:
        resultado = self._controller.restaurar(objeto_id)
        if not resultado.sucesso:
            messagebox.showerror(
                "Nao foi possivel restaurar", resultado.mensagem_erro
            )
            return
        self._atualizar_lista()

    def _excluir_definitivamente(self, objeto_id: int) -> None:
        confirmar = messagebox.askyesno(
            "Excluir definitivamente",
            "Esta acao e irreversivel. Deseja realmente excluir "
            "este objeto de vez, junto com suas tags e relacoes?",
        )
        if not confirmar:
            return

        resultado = self._controller.excluir_definitivamente(objeto_id)
        if not resultado.sucesso:
            messagebox.showerror("Nao foi possivel excluir", resultado.mensagem_erro)
            return
        self._atualizar_lista()
