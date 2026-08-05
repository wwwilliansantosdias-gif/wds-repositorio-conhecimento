"""View do painel de Objeto em Foco + Contexto.

Mostra os detalhes do objeto selecionado e as duas secoes do Contexto
(Relacionamentos, sem score, e Sugestoes Semanticas, com score),
delegando toda a logica ao ObjetoController e ao TagController.

Ao selecionar um item do Contexto, este proprio painel se atualiza
para o novo objeto -- os resultados da pesquisa a esquerda permanecem
intactos (docs/interface-grafica.md).
"""

from __future__ import annotations

from collections.abc import Callable
import os
from typing import Any
from tkinter import messagebox
import webbrowser

import customtkinter as ctk

from controllers.editor_markdown_controller import TIPOS_EDITAVEIS
from controllers.objeto_controller import ObjetoController
from controllers.tag_controller import TagController
from models import Objeto, Tag
from widgets.resultado_item import ResultadoItem
from widgets.tag_chip import TagChip

LIMITE_RESUMO_DETALHE = 2000


class ObjetoView(ctk.CTkScrollableFrame):
    """Exibe o Objeto em Foco e seu Contexto."""

    def __init__(
        self,
        master: Any,
        objeto_controller: ObjetoController,
        tag_controller: TagController,
        ao_selecionar_objeto: Callable[[int], None],
        ao_selecionar_tag: Callable[[str], None],
        ao_editar_objeto: Callable[[int], None],
        **kwargs: Any,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._objeto_controller = objeto_controller
        self._tag_controller = tag_controller
        self._ao_selecionar_objeto = ao_selecionar_objeto
        self._ao_selecionar_tag = ao_selecionar_tag
        self._ao_editar_objeto = ao_editar_objeto
        self._objeto_id_atual: int | None = None

        self.grid_columnconfigure(0, weight=1)

        self.mostrar_espaco_reservado()

    def mostrar_espaco_reservado(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        self._objeto_id_atual = None
        ctk.CTkLabel(
            self,
            text="Selecione um resultado\npara ver os detalhes aqui.",
            text_color="gray60",
        ).grid(row=0, column=0, pady=200)

    def mostrar_objeto(self, objeto_id: int) -> None:
        """Carrega e exibe os detalhes de um objeto especifico."""
        try:
            detalhe = self._objeto_controller.carregar_detalhe(objeto_id)
        except LookupError:
            self.mostrar_espaco_reservado()
            return

        self._objeto_id_atual = objeto_id

        for widget in self.winfo_children():
            widget.destroy()

        linha = 0

        cabecalho_frame = ctk.CTkFrame(self, fg_color="transparent")
        cabecalho_frame.grid(
            row=linha, column=0, sticky="ew", padx=16, pady=(16, 0)
        )
        cabecalho_frame.grid_columnconfigure(0, weight=1)

        eyebrow = f"{detalhe.objeto.tipo}  ·  {detalhe.objeto.data_criacao[:10]}"
        ctk.CTkLabel(
            cabecalho_frame,
            text=eyebrow,
            font=ctk.CTkFont(size=11),
            text_color="gray60",
        ).grid(row=0, column=0, sticky="w")

        coluna_acao = 1
        if detalhe.objeto.tipo in TIPOS_EDITAVEIS:
            ctk.CTkButton(
                cabecalho_frame,
                text="Editar",
                width=80,
                height=24,
                font=ctk.CTkFont(size=11),
                command=lambda: self._ao_editar_objeto(objeto_id),
            ).grid(row=0, column=coluna_acao, sticky="e", padx=(0, 8))
            coluna_acao += 1

        if detalhe.objeto.tipo != "Nota":
            ctk.CTkButton(
                cabecalho_frame,
                text="Abrir Original",
                width=120,
                height=24,
                font=ctk.CTkFont(size=11),
                command=lambda: self._abrir_original(detalhe.objeto),
            ).grid(row=0, column=coluna_acao, sticky="e", padx=(0, 8))
            coluna_acao += 1

        ctk.CTkButton(
            cabecalho_frame,
            text="Mover para Lixeira",
            width=140,
            height=24,
            fg_color="gray40",
            hover_color="gray30",
            font=ctk.CTkFont(size=11),
            command=lambda: self._excluir(objeto_id),
        ).grid(row=0, column=coluna_acao, sticky="e")
        linha += 1

        ctk.CTkLabel(
            self,
            text=detalhe.objeto.titulo,
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w",
            justify="left",
            wraplength=480,
        ).grid(row=linha, column=0, sticky="w", padx=16, pady=(4, 12))
        linha += 1

        tags_frame = ctk.CTkFrame(self, fg_color="transparent")
        tags_frame.grid(row=linha, column=0, sticky="w", padx=16, pady=(0, 16))
        self._renderizar_tags_e_entrada(tags_frame, detalhe.tags)
        linha += 1

        if detalhe.objeto.resumo:
            ctk.CTkLabel(
                self,
                text="Resumo",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="gray60",
                anchor="w",
            ).grid(row=linha, column=0, sticky="w", padx=16, pady=(4, 4))
            linha += 1

            resumo_texto = detalhe.objeto.resumo
            if len(resumo_texto) > LIMITE_RESUMO_DETALHE:
                resumo_texto = resumo_texto[:LIMITE_RESUMO_DETALHE] + "... (truncado)"

            ctk.CTkLabel(
                self,
                text=resumo_texto,
                font=ctk.CTkFont(size=13),
                anchor="w",
                justify="left",
                wraplength=480,
            ).grid(row=linha, column=0, sticky="w", padx=16, pady=(0, 16))
            linha += 1

        linha = self._renderizar_secao_contexto(
            linha,
            titulo="Relacionamentos",
            objetos_com_score=[(obj, None) for obj in detalhe.relacionamentos],
            mensagem_vazio="Nenhum relacionamento cadastrado.",
        )

        linha = self._renderizar_secao_contexto(
            linha,
            titulo="Sugestões Semânticas",
            objetos_com_score=[(s.objeto, s.score) for s in detalhe.sugestoes],
            mensagem_vazio="Nenhuma sugestão encontrada.",
        )

    def _renderizar_secao_contexto(
        self,
        linha: int,
        titulo: str,
        objetos_com_score: list[tuple[Objeto, float | None]],
        mensagem_vazio: str,
    ) -> int:
        ctk.CTkLabel(
            self,
            text=titulo,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray60",
            anchor="w",
        ).grid(row=linha, column=0, sticky="w", padx=16, pady=(8, 4))
        linha += 1

        if not objetos_com_score:
            ctk.CTkLabel(
                self, text=mensagem_vazio, text_color="gray60"
            ).grid(row=linha, column=0, sticky="w", padx=16, pady=(0, 8))
            return linha + 1

        for objeto, score in objetos_com_score:
            tags = self._tag_controller.listar_por_objeto(objeto.id)
            item = ResultadoItem(
                self,
                objeto=objeto,
                tags=tags,
                score=score,
                ao_selecionar=self._ao_selecionar_objeto,
            )
            item.grid(row=linha, column=0, sticky="ew", padx=16, pady=(0, 8))
            linha += 1

        return linha

    def _renderizar_tags_e_entrada(
        self,
        container: ctk.CTkFrame,
        tags: list[Tag],
    ) -> None:
        coluna = 0
        for tag in tags:
            chip = TagChip(
                container,
                tag,
                ao_remover=self._remover_tag,
                ao_selecionar=self._ao_selecionar_tag,
            )
            chip.grid(row=0, column=coluna, padx=(0, 6))
            coluna += 1

        entrada = ctk.CTkEntry(
            container, placeholder_text="+ tag", width=90, height=24
        )
        entrada.grid(row=0, column=coluna, padx=(0, 0))
        entrada.bind("<Return>", lambda evento: self._adicionar_tag(entrada))

    def _adicionar_tag(self, entrada: ctk.CTkEntry) -> None:
        if self._objeto_id_atual is None:
            return
        nome = entrada.get()
        resultado = self._tag_controller.adicionar_tag(self._objeto_id_atual, nome)
        if resultado.sucesso:
            self.mostrar_objeto(self._objeto_id_atual)

    def _remover_tag(self, tag_id: int) -> None:
        if self._objeto_id_atual is None:
            return
        self._tag_controller.remover_tag(self._objeto_id_atual, tag_id)
        self.mostrar_objeto(self._objeto_id_atual)

    def _excluir(self, objeto_id: int) -> None:
        """Move o objeto para a lixeira e limpa o painel, ja que o
        objeto em foco deixou de estar ativo."""
        self._objeto_controller.excluir(objeto_id)
        self.mostrar_espaco_reservado()

    @staticmethod
    def _abrir_original(objeto: Objeto) -> None:
        """Abre o arquivo ou link associado ao objeto no sistema."""
        try:
            if objeto.tipo == "Link":
                webbrowser.open(objeto.caminho)
                return

            os.startfile(objeto.caminho)
        except OSError as erro:
            messagebox.showerror("Não foi possível abrir o original", str(erro))
