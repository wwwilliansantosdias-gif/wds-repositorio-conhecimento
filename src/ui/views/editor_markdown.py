"""Janela do Editor Markdown -- tela propria incluida no MVP
(docs/interface-grafica.md).

Permite editar o conteudo fisico de uma Nota (tipo "Nota" ou
"Markdown"), delegando toda a logica de carregar/salvar ao
``EditorMarkdownController``. Abre como janela separada (modal), sem
substituir a janela principal -- ao fechar, o usuario volta exatamente
para onde estava, seguindo o mesmo padrao ja usado pela Lixeira.

Nao pretende substituir editores especializados: e um CTkTextbox
simples, sem realce de sintaxe ou pre-visualizacao.

Salvar roda em segundo plano (tarefas_segundo_plano): reindexar o
vetor semantico da nota envolve o modelo de IA, lento o bastante para
travar a janela por um instante se rodasse na thread principal. O
texto e lido do CTkTextbox ANTES de entrar na tarefa de segundo plano
-- widgets do Tkinter so podem ser lidos/alterados na thread
principal, entao a tarefa em si so recebe o texto ja capturado, nunca
o widget.
"""

from __future__ import annotations

from collections.abc import Callable
from tkinter import messagebox
from typing import Any

import customtkinter as ctk

from controllers.editor_markdown_controller import EditorMarkdownController
from tarefas_segundo_plano import executar_em_segundo_plano


class EditorMarkdownWindow(ctk.CTkToplevel):
    """Janela modal para editar o conteudo de uma Nota."""

    def __init__(
        self,
        master: Any,
        editor_markdown_controller: EditorMarkdownController,
        objeto_id: int,
        ao_salvar: Callable[[int], None] | None = None,
    ) -> None:
        super().__init__(master)
        self._controller = editor_markdown_controller
        self._objeto_id = objeto_id
        self._ao_salvar = ao_salvar
        self._texto_salvo: str = ""

        self.geometry("640x520")
        self.transient(master)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        try:
            conteudo = self._controller.carregar(objeto_id)
        except (LookupError, ValueError, OSError) as erro:
            messagebox.showerror("Nao foi possivel abrir a nota", str(erro))
            self.destroy()
            return

        self.title(f"Editor Markdown - {conteudo.objeto.titulo}")
        self._texto_salvo = conteudo.texto

        self._caixa_texto = ctk.CTkTextbox(self, wrap="word", font=("", 13))
        self._caixa_texto.grid(
            row=1, column=0, sticky="nsew", padx=16, pady=(8, 8)
        )
        self._caixa_texto.insert("1.0", conteudo.texto)

        self._rotulo_status = ctk.CTkLabel(
            self, text="", text_color="gray60", anchor="w"
        )
        self._rotulo_status.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 0))

        botoes = ctk.CTkFrame(self, fg_color="transparent")
        botoes.grid(row=2, column=0, sticky="e", padx=16, pady=(0, 16))
        self._botao_fechar = ctk.CTkButton(
            botoes,
            text="Fechar",
            fg_color="gray50",
            width=100,
            height=32,
            command=self._fechar,
        )
        self._botao_fechar.grid(row=0, column=0, padx=6)
        self._botao_salvar = ctk.CTkButton(
            botoes,
            text="Salvar",
            width=100,
            height=32,
            command=self._salvar,
        )
        self._botao_salvar.grid(row=0, column=1, padx=6)

        self._caixa_texto.bind("<Control-s>", lambda evento: self._salvar())
        self.protocol("WM_DELETE_WINDOW", self._fechar)

        self.lift()
        self.focus_force()
        self.grab_set()

    def _salvar(self) -> None:
        texto = self._caixa_texto.get("1.0", "end-1c")

        self._rotulo_status.configure(text="Salvando...")
        self._botao_salvar.configure(state="disabled")

        executar_em_segundo_plano(
            self,
            lambda: self._controller.salvar(self._objeto_id, texto),
            ao_concluir=lambda resultado: self._ao_terminar_salvar(resultado, texto),
            ao_falhar=self._ao_falhar_salvar,
        )

    def _ao_terminar_salvar(self, resultado, texto: str) -> None:
        self._botao_salvar.configure(state="normal")

        if not resultado.sucesso:
            self._rotulo_status.configure(text="")
            messagebox.showerror("Nao foi possivel salvar", resultado.mensagem_erro)
            return

        self._texto_salvo = texto
        self._rotulo_status.configure(text="Salvo.")

        if self._ao_salvar is not None:
            self._ao_salvar(self._objeto_id)

    def _ao_falhar_salvar(self, erro: Exception) -> None:
        self._botao_salvar.configure(state="normal")
        self._rotulo_status.configure(text="")
        messagebox.showerror("Erro inesperado ao salvar", str(erro))

    def _fechar(self) -> None:
        texto_atual = self._caixa_texto.get("1.0", "end-1c")
        if texto_atual != self._texto_salvo:
            descartar = messagebox.askyesno(
                "Alteracoes nao salvas",
                "Existem alteracoes nao salvas nesta nota. "
                "Deseja fechar mesmo assim e descarta-las?",
            )
            if not descartar:
                return
        self.destroy()
