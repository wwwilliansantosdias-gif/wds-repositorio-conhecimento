"""Janela de Configuracoes -- tela propria do MVP (Issue 27, EPIC 7).

Duas preferencias, conforme decidido em ConfigService: tema da
interface e quantidade de resultados semanticos por busca. Abre como
janela separada (modal), mesmo padrao ja usado por Lixeira, Backup e
Editor Markdown.
"""

from __future__ import annotations

from tkinter import messagebox
from typing import Any

import customtkinter as ctk

from controllers.configuracoes_controller import ConfiguracoesController
from services.config_service import LIMITE_MAXIMO, LIMITE_MINIMO, TEMAS_VALIDOS


class ConfiguracoesWindow(ctk.CTkToplevel):
    """Janela modal para editar as preferencias do usuario."""

    def __init__(
        self,
        master: Any,
        configuracoes_controller: ConfiguracoesController,
    ) -> None:
        super().__init__(master)
        self.transient(master)
        self.lift()
        self.focus_force()
        self.grab_set()
        self.title("Configurações")
        self.geometry("420x320")
        self._controller = configuracoes_controller

        self.grid_columnconfigure(0, weight=1)

        config_atual = self._controller.carregar()

        ctk.CTkLabel(
            self,
            text="Tema da interface",
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 4))

        self._tema_var = ctk.StringVar(value=config_atual.tema)
        ctk.CTkSegmentedButton(
            self,
            values=list(TEMAS_VALIDOS),
            variable=self._tema_var,
        ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            self,
            text="Quantidade de resultados semânticos por busca",
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 4))

        ctk.CTkLabel(
            self,
            text=f"Entre {LIMITE_MINIMO} e {LIMITE_MAXIMO}. Afeta só a busca por "
            "sentido; a busca por palavra exata não tem limite.",
            text_color="gray60",
            anchor="w",
            justify="left",
            wraplength=380,
        ).grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 8))

        self._limite_entry = ctk.CTkEntry(self, width=80)
        self._limite_entry.insert(0, str(config_atual.limite_resultados_semanticos))
        self._limite_entry.grid(row=4, column=0, sticky="w", padx=20, pady=(0, 24))

        ctk.CTkButton(
            self,
            text="Salvar",
            height=36,
            command=self._salvar,
        ).grid(row=5, column=0, sticky="e", padx=20, pady=(0, 20))

    def _salvar(self) -> None:
        tema = self._tema_var.get()

        texto_limite = self._limite_entry.get().strip()
        try:
            limite = int(texto_limite)
        except ValueError:
            messagebox.showerror(
                "Valor inválido",
                f"'{texto_limite}' não é um número inteiro válido.",
            )
            return

        resultado = self._controller.salvar(tema, limite)
        if not resultado.sucesso:
            messagebox.showerror("Não foi possível salvar", resultado.mensagem_erro)
            return

        ctk.set_appearance_mode(
            {"Sistema": "system", "Claro": "light", "Escuro": "dark"}[tema]
        )
        messagebox.showinfo(
            "Configurações salvas",
            "O tema foi aplicado imediatamente. A nova quantidade de "
            "resultados semânticos vale a partir da próxima pesquisa.",
        )
        self.destroy()
