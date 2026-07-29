"""View da area de Resultados.

Renderiza a lista de resultados de uma pesquisa (textual e/ou
semantica), delegando a logica de busca ao PesquisaController e a
busca de tags ao TagController. A busca em si e disparada pela
Toolbar (Barra Superior) -- esta view apenas recebe o termo e mostra
os resultados; nao possui campo de busca proprio.

Tambem atende a Biblioteca (docs/interface-grafica.md): listar_todos()
reaproveita o mesmo componente de lista (ResultadoItem) para mostrar
todos os objetos ativos, sem termo de busca.

A busca com termo roda em segundo plano
(tarefas_segundo_plano.executar_em_segundo_plano): envolve o modelo de
busca semantica, lento o bastante para travar a janela por um instante
se rodasse na thread principal. listar_todos() nao roda em segundo
plano -- e so uma leitura direta do banco, sem o modelo de IA
envolvido, rapida o bastante para nao precisar disso.

Notifica um callback externo quando um resultado e selecionado; nao
decide sozinha o que acontece depois do clique.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from controllers.pesquisa_controller import PesquisaController
from controllers.tag_controller import TagController
from tarefas_segundo_plano import executar_em_segundo_plano
from widgets.resultado_item import ResultadoItem


class PesquisaView(ctk.CTkFrame):
    """Exibe os resultados retornados pelo controller de pesquisa."""

    def __init__(
        self,
        master: Any,
        pesquisa_controller: PesquisaController,
        tag_controller: TagController,
        ao_selecionar_objeto: Callable[[int], None],
        **kwargs: Any,
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
        """Executa a busca e atualiza a lista de resultados exibida.

        Termo vazio nao precisa de segundo plano -- o controller
        devolve lista vazia sem tocar no modelo de IA, entao o
        resultado ja volta instantaneo.
        """
        if not termo.strip():
            self._renderizar([], "Digite um termo na barra acima para pesquisar o Acervo.")
            return

        self._mostrar_mensagem("Buscando...")
        executar_em_segundo_plano(
            self,
            lambda: self._pesquisa_controller.pesquisar(termo),
            ao_concluir=lambda resultados: self._renderizar(
                resultados, "Nenhum resultado encontrado."
            ),
            ao_falhar=lambda erro: self._mostrar_mensagem(
                f"Nao foi possivel buscar: {erro}"
            ),
        )

    def listar_todos(self) -> None:
        """Mostra todos os Objetos de Conhecimento ativos (Biblioteca).

        Reaproveita o mesmo componente de lista da Pesquisa
        (docs/interface-grafica.md, secao "Biblioteca"), so troca a
        origem dos resultados.
        """
        resultados = self._pesquisa_controller.listar_todos()
        self._renderizar(resultados, "O Acervo ainda nao tem nenhum objeto.")

    def _renderizar(self, resultados: list, mensagem_vazio: str) -> None:
        for widget in self._lista_scroll.winfo_children():
            widget.destroy()

        if not resultados:
            self._mostrar_mensagem(mensagem_vazio)
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
        """Mostra uma mensagem central na lista, substituindo qualquer
        conteudo anterior (resultados ou outra mensagem).

        Sem a limpeza, chamar isso mais de uma vez (ex.: "Buscando..."
        seguido do resultado final) empilhava labels umas sobre as
        outras em vez de substituir -- so nao aparecia antes porque,
        ate a busca em segundo plano existir, este metodo era chamado
        uma unica vez, no __init__.
        """
        for widget in self._lista_scroll.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self._lista_scroll, text=texto, text_color="gray60").grid(
            row=0, column=0, pady=40
        )
