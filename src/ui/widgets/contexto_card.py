"""Widget de card para a área de Contexto.

Define o contêiner visual reutilizável destinado à apresentação de itens
de relacionamento ou sugestões semânticas do Objeto em Foco.
"""

from __future__ import annotations

from typing import Any

import customtkinter as ctk


class ContextoCard(ctk.CTkFrame):
    """Estrutura visual reservada para um item da área de Contexto."""

    def __init__(self, master: Any, **kwargs: Any) -> None:
        super().__init__(master, corner_radius=8, **kwargs)
