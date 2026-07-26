"""Dialogo modal simples para coletar um ou mais campos de texto.

Usado pelo menu "Novo Objeto" para Cadastrar Link (URL + titulo) e
Nova Nota (titulo).
"""

from __future__ import annotations

from typing import Any

import customtkinter as ctk


class DialogoTexto(ctk.CTkToplevel):
    """Coleta campos de texto em uma janela modal."""

    def __init__(self, master: Any, titulo: str, campos: list[str]) -> None:
        super().__init__(master)
        self.title(titulo)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.grid_columnconfigure(0, weight=1)

        self.resultado: dict[str, str] | None = None
        self._entradas: dict[str, ctk.CTkEntry] = {}

        linha = 0
        for campo in campos:
            ctk.CTkLabel(self, text=campo).grid(
                row=linha,
                column=0,
                sticky="w",
                padx=16,
                pady=(16 if linha == 0 else 8, 0),
            )
            linha += 1
            entrada = ctk.CTkEntry(self, width=300)
            entrada.grid(row=linha, column=0, padx=16, sticky="ew")
            self._entradas[campo] = entrada
            linha += 1

        botoes = ctk.CTkFrame(self, fg_color="transparent")
        botoes.grid(row=linha, column=0, pady=16)
        ctk.CTkButton(
            botoes,
            text="Cancelar",
            fg_color="gray50",
            width=100,
            height=32,
            command=self._cancelar,
        ).grid(row=0, column=0, padx=6)
        ctk.CTkButton(
            botoes,
            text="Confirmar",
            width=100,
            height=32,
            command=self._confirmar,
        ).grid(row=0, column=1, padx=6)

        if self._entradas:
            primeira = next(iter(self._entradas.values()))
            primeira.focus_set()
            primeira.bind("<Return>", lambda evento: self._confirmar())

        self.protocol("WM_DELETE_WINDOW", self._cancelar)

    def _confirmar(self) -> None:
        self.resultado = {
            campo: entrada.get() for campo, entrada in self._entradas.items()
        }
        self.destroy()

    def _cancelar(self) -> None:
        self.resultado = None
        self.destroy()

    def aguardar_resultado(self) -> dict[str, str] | None:
        """Bloqueia ate o dialogo ser fechado (Confirmar ou Cancelar)."""
        self.master.wait_window(self)
        return self.resultado
