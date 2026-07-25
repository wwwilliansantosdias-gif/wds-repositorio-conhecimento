"""View da area de Resultados.

Renderiza a lista de resultados de uma pesquisa (textual e/ou
semantica), delegando a logica de busca ao PesquisaController e a
busca de tags ao TagController. A busca em si e disparada pela
Toolbar (Barra Superior) -- esta view apenas recebe o termo e mostra
os resultados; nao possui campo de busca proprio.

Notifica um callback externo quando um resultado e selecionado; nao
decide sozinha o que acontece depois do clique.
"""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from controllers.pesquisa_controller import PesquisaController
from controllers.tag_controller import TagController
from widgets.resultado_item import ResultadoItem


class PesquisaView(ctk.CTkFrame):
    def __init__(
        self,
        master,
        pesquisa_controller: PesquisaController,
        tag_controller: TagController,
        ao_selecionar_objeto: Callable[[int], None],
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._pesquisa_controller = pesquisa_controller
        self._tag_controller = tag_controller
        self._ao_selecionar_objeto = ao_selecionar_objeto

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._lista_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._lista_scroll.grid(row=0, column=0, sticky="nsew")
        self._lista_scroll.grid_columnconfigure(0, weight=1)

        self._mostrar_mensagem("Digite um termo na barra acima para pesquisar o Acervo.")

    def pesquisar(self, termo: str) -> None:
        """Executa a busca e atualiza a lista de resultados exibida."""
        for widget in self._lista_scroll.winfo_children():
            widget.destroy()

        resultados = self._pesquisa_controller.pesquisar(termo)

        if not resultados:
            mensagem = (
                "Nenhum resultado encontrado."
                if termo.strip()
                else "Digite um termo na barra acima para pesquisar o Acervo."
            )
            self._mostrar_mensagem(mensagem)
            return

        for indice, resultado in enumerate(resultados):
            tags = self._tag_controller.listar_por_objeto(resultado.objeto.id)
            item = ResultadoItem(
                self._lista_scroll,
                objeto=resultado.objeto,
                tags=tags,
                score=resultado.score,
                ao_selecionar=self._ao_selecionar_objeto,
            )
            item.grid(row=indice, column=0, sticky="ew", pady=(0, 8))

    def _mostrar_mensagem(self, texto: str) -> None:
        ctk.CTkLabel(self._lista_scroll, text=texto, text_color="gray60").grid(
            row=0, column=0, pady=40
        )
