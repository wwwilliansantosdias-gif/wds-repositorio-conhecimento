"""Menu de criacao "Novo Objeto", acionado pelo botao na Barra Superior.

Oferece as quatro formas de criacao suportadas por
NovoObjetoController -- Importar PDF, Importar Markdown, Cadastrar
Link, Nova Nota -- conforme decidido em docs/interface-grafica.md.
Cada opcao coleta a entrada necessaria (seletor de arquivo nativo ou
um DialogoTexto) e delega ao controller, traduzindo o resultado em
feedback simples (mensagem de erro ou o novo objeto criado).
"""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Any

from controllers.novo_objeto_controller import NovoObjetoController, ResultadoCriacao
from widgets.dialogo_texto import DialogoTexto


class NovoObjetoMenu:
    """Controla o menu suspenso e os fluxos de criacao de objetos."""

    def __init__(
        self,
        master: Any,
        novo_objeto_controller: NovoObjetoController,
        ao_criar_objeto: Callable[[int], None],
    ) -> None:
        self._master = master
        self._controller = novo_objeto_controller
        self._ao_criar_objeto = ao_criar_objeto

        self._menu = tk.Menu(master, tearoff=0)
        self._menu.add_command(label="Importar PDF", command=self._importar_pdf)
        self._menu.add_command(
            label="Importar Markdown", command=self._importar_markdown
        )
        self._menu.add_command(label="Cadastrar Link", command=self._cadastrar_link)
        self._menu.add_command(label="Nova Nota", command=self._nova_nota)

    def abrir(self, x: int, y: int) -> None:
        """Exibe o menu na posicao indicada (coordenadas de tela)."""
        try:
            self._menu.tk_popup(x, y)
        finally:
            self._menu.grab_release()

    def _importar_pdf(self) -> None:
        caminho = filedialog.askopenfilename(
            title="Selecionar PDF", filetypes=[("PDF", "*.pdf")]
        )
        if not caminho:
            return
        self._tratar_resultado(self._controller.importar_pdf(caminho))

    def _importar_markdown(self) -> None:
        caminho = filedialog.askopenfilename(
            title="Selecionar Markdown", filetypes=[("Markdown", "*.md")]
        )
        if not caminho:
            return
        self._tratar_resultado(self._controller.importar_markdown(caminho))

    def _cadastrar_link(self) -> None:
        dialogo = DialogoTexto(
            self._master, "Cadastrar Link", ["URL", "Titulo (opcional)"]
        )
        dados = dialogo.aguardar_resultado()
        if dados is None:
            return
        titulo = dados["Titulo (opcional)"].strip() or None
        self._tratar_resultado(
            self._controller.cadastrar_link(dados["URL"], titulo=titulo)
        )

    def _nova_nota(self) -> None:
        dialogo = DialogoTexto(self._master, "Nova Nota", ["Titulo"])
        dados = dialogo.aguardar_resultado()
        if dados is None:
            return
        self._tratar_resultado(self._controller.criar_nota(dados["Titulo"]))

    def _tratar_resultado(self, resultado: ResultadoCriacao) -> None:
        if resultado.sucesso:
            self._ao_criar_objeto(resultado.objeto.id)
        else:
            messagebox.showerror(
                "Nao foi possivel criar o objeto", resultado.mensagem_erro
            )
