"""Widget de um item na lista de resultados (Pesquisa/Biblioteca/Lixeira).

Mostra titulo, tipo, resumo curto, tags e, quando disponivel, o score
de similaridade semantica. Notifica um callback externo ao ser
selecionado -- nao decide sozinho o que acontece depois do clique.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from models import Objeto, Tag

SCORE_FORTE = 75.0
SCORE_FRACO = 50.0

COR_SCORE_FORTE = ("#0F8F7E", "#3DDBC0")
COR_SCORE_MEDIO = "#4FA9A0"
COR_SCORE_FRACO = ("gray75", "gray40")


def estilo_por_score(score: float) -> tuple[Any, Any | None]:
    """Devolve (cor do score, cor do titulo) para um score de sugestao.

    Faixas (docs/wds-1.2-planejamento.md, item A.2): >= 75 destaca o
    score; de 50 a 75 mantem o visual padrao; < 50 apaga score e titulo
    alem do gray60 usado em texto secundario. Cor do titulo None
    significa a cor padrao do tema.
    """
    if score >= SCORE_FORTE:
        return COR_SCORE_FORTE, None
    if score >= SCORE_FRACO:
        return COR_SCORE_MEDIO, None
    return COR_SCORE_FRACO, COR_SCORE_FRACO


class ResultadoItem(ctk.CTkFrame):
    """Apresenta um objeto recuperado em uma lista de resultados."""

    def __init__(
        self,
        master: Any,
        objeto: Objeto,
        tags: list[Tag],
        ao_selecionar: Callable[[int], None],
        score: float | None = None,
        trecho: str | None = None,
        peso_visual_por_score: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, corner_radius=8, **kwargs)
        self._objeto_id = objeto.id
        self._ao_selecionar = ao_selecionar

        self.grid_columnconfigure(0, weight=1)

        cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        cabecalho.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 0))
        cabecalho.grid_columnconfigure(0, weight=1)

        cor_score = COR_SCORE_MEDIO
        opcoes_titulo: dict[str, Any] = {}
        if peso_visual_por_score and score is not None:
            cor_score, cor_titulo = estilo_por_score(score)
            if cor_titulo is not None:
                opcoes_titulo["text_color"] = cor_titulo

        titulo_label = ctk.CTkLabel(
            cabecalho,
            text=objeto.titulo,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
            **opcoes_titulo,
        )
        titulo_label.grid(row=0, column=0, sticky="w")

        if score is not None:
            ctk.CTkLabel(
                cabecalho,
                text=f"{score:.0f}%",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=cor_score,
            ).grid(row=0, column=1, padx=(8, 0))

        ctk.CTkLabel(
            self,
            text=objeto.tipo,
            font=ctk.CTkFont(size=10),
            text_color="gray60",
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=12)

        linha_tags = 2
        if objeto.resumo:
            resumo_texto = objeto.resumo.strip().replace("\n", " ")
            if len(resumo_texto) > 140:
                resumo_texto = resumo_texto[:140].rstrip() + "..."
            ctk.CTkLabel(
                self,
                text=resumo_texto,
                font=ctk.CTkFont(size=12),
                anchor="w",
                justify="left",
                wraplength=360,
            ).grid(row=2, column=0, sticky="w", padx=12, pady=(4, 0))
            linha_tags += 1

        if trecho:
            rotulo_trecho = "Contexto:" if score is not None else "Trecho encontrado:"
            ctk.CTkLabel(
                self,
                text=f"{rotulo_trecho} {trecho}",
                font=ctk.CTkFont(size=11),
                text_color="gray60",
                anchor="w",
                justify="left",
                wraplength=360,
            ).grid(row=linha_tags, column=0, sticky="w", padx=12, pady=(4, 0))
            linha_tags += 1

        if tags:
            tags_texto = "  ".join(f"#{tag.nome}" for tag in tags)
            ctk.CTkLabel(
                self,
                text=tags_texto,
                font=ctk.CTkFont(size=11),
                text_color="#5AADA3",
                anchor="w",
            ).grid(
                row=linha_tags, column=0, sticky="w", padx=12, pady=(4, 10)
            )
        else:
            ctk.CTkLabel(self, text="", height=1).grid(
                row=linha_tags, column=0, pady=(0, 10)
            )

        for widget in (self, cabecalho, titulo_label):
            widget.bind("<Button-1>", self._selecionar)

    def _selecionar(self, _evento: object | None = None) -> None:
        self._ao_selecionar(self._objeto_id)
