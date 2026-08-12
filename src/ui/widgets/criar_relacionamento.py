"""Widget inline para criar relacionamentos entre Objetos."""

from __future__ import annotations

from collections.abc import Callable
from tkinter import messagebox
from typing import Any

import customtkinter as ctk

from controllers.relacao_controller import RelacaoController, ResultadoCriarRelacionamento
from models import Objeto
from tarefas_segundo_plano import executar_em_segundo_plano


class CriarRelacionamento(ctk.CTkFrame):
    """Conduz o fluxo inline de busca e criação de relacionamento."""

    ESTADO_OCIOSO = "ocioso"
    ESTADO_BUSCANDO = "buscando"
    ESTADO_RESULTADOS = "resultados"
    ESTADO_TIPO = "tipo"

    def __init__(
        self,
        master: Any,
        relacao_controller: RelacaoController,
        origem_id: int,
        ao_criar_relacao: Callable[[int], None],
        **kwargs: Any,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._relacao_controller = relacao_controller
        self._origem_id = origem_id
        self._ao_criar_relacao = ao_criar_relacao
        self._termo_busca = ""
        self._objeto_destino: Objeto | None = None
        self._criar_novo = False
        self._entrada_busca: ctk.CTkEntry | None = None
        self._combo_tipo: ctk.CTkComboBox | None = None
        self.estado = self.ESTADO_OCIOSO

        self.mostrar_ocioso()

    def mostrar_ocioso(self) -> None:
        """Exibe apenas a ação inicial do fluxo."""
        self._limpar()
        self.estado = self.ESTADO_OCIOSO
        ctk.CTkButton(
            self,
            text="+ Relacionar",
            width=100,
            height=24,
            font=ctk.CTkFont(size=11),
            command=self.mostrar_busca,
        ).grid(row=0, column=0)

    def mostrar_busca(self) -> None:
        """Exibe a entrada de busca e a ação de cancelar."""
        self._limpar()
        self.estado = self.ESTADO_BUSCANDO
        self._entrada_busca = ctk.CTkEntry(
            self, placeholder_text="Buscar objeto", width=180, height=24
        )
        self._entrada_busca.grid(row=0, column=0, padx=(0, 4))
        self._entrada_busca.bind("<Return>", self._buscar)
        self._entrada_busca.focus_set()
        ctk.CTkButton(
            self,
            text="x",
            width=24,
            height=24,
            fg_color="transparent",
            hover_color="gray40",
            command=self.mostrar_ocioso,
        ).grid(row=0, column=1)

    def _buscar(self, _evento: object | None = None) -> None:
        if self._entrada_busca is None:
            return

        self._termo_busca = self._entrada_busca.get().strip()
        resultados = self._relacao_controller.buscar_objetos_para_relacionar(
            self._termo_busca, self._origem_id
        )
        self._mostrar_resultados(resultados)

    def _mostrar_resultados(self, resultados: list[Objeto]) -> None:
        self._limpar()
        self.estado = self.ESTADO_RESULTADOS

        if not resultados:
            ctk.CTkLabel(self, text="Nenhum objeto encontrado.", text_color="gray60").grid(
                row=0, column=0, sticky="w", pady=(0, 4)
            )

        for linha, objeto in enumerate(resultados):
            ctk.CTkButton(
                self,
                text=f"{objeto.titulo} · {objeto.tipo}",
                anchor="w",
                fg_color="transparent",
                hover_color="gray40",
                text_color=("gray10", "gray90"),
                command=lambda objeto=objeto: self._selecionar_objeto(objeto),
            ).grid(row=linha, column=0, sticky="ew", pady=(0, 2))

        if self._termo_busca:
            ctk.CTkButton(
                self,
                text=f"+ Criar novo objeto: '{self._termo_busca}'",
                anchor="w",
                fg_color="transparent",
                hover_color="gray40",
                text_color="#4FA9A0",
                command=self._selecionar_novo_objeto,
            ).grid(row=len(resultados), column=0, sticky="ew")

    def _selecionar_objeto(self, objeto: Objeto) -> None:
        self._objeto_destino = objeto
        self._criar_novo = False
        self._mostrar_tipo_relacao(objeto.titulo)

    def _selecionar_novo_objeto(self) -> None:
        self._objeto_destino = None
        self._criar_novo = True
        self._mostrar_tipo_relacao(self._termo_busca)

    def _mostrar_tipo_relacao(self, titulo_destino: str) -> None:
        self._limpar()
        self.estado = self.ESTADO_TIPO
        ctk.CTkLabel(
            self,
            text=titulo_destino,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))
        self._combo_tipo = ctk.CTkComboBox(
            self,
            values=self._relacao_controller.listar_tipos_usados(),
            width=180,
            height=24,
        )
        self._combo_tipo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        ctk.CTkButton(
            self,
            text="Confirmar",
            width=80,
            height=24,
            font=ctk.CTkFont(size=11),
            command=self._confirmar,
        ).grid(row=2, column=0, sticky="w", padx=(0, 4))
        ctk.CTkButton(
            self,
            text="Cancelar",
            width=70,
            height=24,
            fg_color="gray40",
            hover_color="gray30",
            font=ctk.CTkFont(size=11),
            command=self.mostrar_ocioso,
        ).grid(row=2, column=1, sticky="w")

    def _confirmar(self) -> None:
        if self._combo_tipo is None:
            return

        tipo_relacao = self._combo_tipo.get()
        if self._criar_novo:
            tarefa = lambda: self._relacao_controller.criar_objeto_e_relacionar(
                self._origem_id, self._termo_busca, tipo_relacao
            )
        elif self._objeto_destino is not None:
            tarefa = lambda: self._relacao_controller.criar(
                self._origem_id, self._objeto_destino.id, tipo_relacao
            )
        else:
            return

        executar_em_segundo_plano(
            self,
            tarefa,
            ao_concluir=self._ao_terminar_criacao,
            ao_falhar=self._ao_falhar_criacao,
        )

    def _ao_terminar_criacao(self, resultado: ResultadoCriarRelacionamento) -> None:
        if not resultado.sucesso:
            messagebox.showerror(
                "Não foi possível criar o relacionamento", resultado.mensagem_erro
            )
            return

        self.mostrar_ocioso()
        self._ao_criar_relacao(self._origem_id)

    @staticmethod
    def _ao_falhar_criacao(erro: Exception) -> None:
        messagebox.showerror("Erro inesperado ao criar relacionamento", str(erro))

    def _limpar(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
