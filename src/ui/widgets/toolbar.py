"""Widget da Barra Superior.

Contem a identificacao do WDS, o campo de pesquisa (sempre visivel,
ancora da navegacao), o botao Novo Objeto e o acesso a Biblioteca, a
Lixeira, ao Backup e as Configuracoes, conforme
docs/interface-grafica.md.

Decisao (nao especificada anteriormente, resolvida aqui): o acesso a
Biblioteca, a Lixeira, ao Backup e as Configuracoes sao pequenos
botoes na Barra Superior. Lixeira, Backup e Configuracoes abrem como
janela separada; Biblioteca reaproveita a propria area de Resultados
(mesmo componente de lista da Pesquisa), entao nao abre uma janela
nova.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from widgets.search_bar import SearchBar


NEUTRAL_NAVIGATION_COLOR = "gray40"
NEUTRAL_NAVIGATION_HOVER_COLOR = "gray30"


def _acervo_theme_color(name: str) -> list[str]:
    """Devolve uma cor da identidade carregada no tema do Acervo."""
    return ctk.ThemeManager.theme["WDS"][name]


class Toolbar(ctk.CTkFrame):
    """Compõe a barra superior de navegação do WDS."""

    def __init__(
        self,
        master: Any,
        ao_pesquisar: Callable[[str], None],
        ao_clicar_novo_objeto: Callable[[int, int], None],
        ao_clicar_lixeira: Callable[[], None],
        ao_clicar_backup: Callable[[], None],
        ao_clicar_biblioteca: Callable[[], None],
        ao_clicar_configuracoes: Callable[[], None],
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master,
            corner_radius=0,
            fg_color=_acervo_theme_color("accent_fg_color"),
            **kwargs,
        )

        self.grid_columnconfigure(1, weight=1)

        titulo = ctk.CTkLabel(
            self,
            text="WDS",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=_acervo_theme_color("accent_text_color"),
        )
        titulo.grid(row=0, column=0, padx=(16, 24), pady=12)

        self.search_bar = SearchBar(self, ao_pesquisar=ao_pesquisar)
        self.search_bar.grid(row=0, column=1, sticky="ew", pady=12)

        self.botao_biblioteca = ctk.CTkButton(
            self,
            text="Biblioteca",
            width=100,
            height=36,
            fg_color=NEUTRAL_NAVIGATION_COLOR,
            hover_color=NEUTRAL_NAVIGATION_HOVER_COLOR,
            command=lambda: self._acionar_navegacao("biblioteca", ao_clicar_biblioteca),
        )
        self.botao_biblioteca.grid(row=0, column=2, padx=(16, 8), pady=12)

        self.botao_lixeira = ctk.CTkButton(
            self,
            text="Lixeira",
            width=90,
            height=36,
            fg_color=NEUTRAL_NAVIGATION_COLOR,
            hover_color=NEUTRAL_NAVIGATION_HOVER_COLOR,
            command=lambda: self._acionar_navegacao("lixeira", ao_clicar_lixeira),
        )
        self.botao_lixeira.grid(row=0, column=3, padx=(0, 8), pady=12)

        self.botao_backup = ctk.CTkButton(
            self,
            text="Backup",
            width=90,
            height=36,
            fg_color=NEUTRAL_NAVIGATION_COLOR,
            hover_color=NEUTRAL_NAVIGATION_HOVER_COLOR,
            command=lambda: self._acionar_navegacao("backup", ao_clicar_backup),
        )
        self.botao_backup.grid(row=0, column=4, padx=(0, 8), pady=12)

        self.botao_configuracoes = ctk.CTkButton(
            self,
            text="Configurações",
            width=110,
            height=36,
            fg_color=NEUTRAL_NAVIGATION_COLOR,
            hover_color=NEUTRAL_NAVIGATION_HOVER_COLOR,
            command=lambda: self._acionar_navegacao(
                "configuracoes", ao_clicar_configuracoes
            ),
        )
        self.botao_configuracoes.grid(row=0, column=5, padx=(0, 8), pady=12)

        self.botao_novo_objeto = ctk.CTkButton(
            self,
            text="+ Novo Objeto",
            width=140,
            height=36,
        )
        self.botao_novo_objeto.grid(row=0, column=6, padx=(0, 16), pady=12)
        self.botao_novo_objeto.bind(
            "<Button-1>",
            lambda evento: ao_clicar_novo_objeto(evento.x_root, evento.y_root),
        )

        self._botoes_navegacao = {
            "biblioteca": self.botao_biblioteca,
            "lixeira": self.botao_lixeira,
            "backup": self.botao_backup,
            "configuracoes": self.botao_configuracoes,
        }

    def _acionar_navegacao(
        self, destino: str, acao: Callable[[], None]
    ) -> None:
        """Destaca somente o item de navegação acionado."""
        for nome, botao in self._botoes_navegacao.items():
            if nome == destino:
                botao.configure(
                    fg_color=_acervo_theme_color("accent_fg_color"),
                    hover_color=_acervo_theme_color("accent_hover_color"),
                    text_color=_acervo_theme_color("accent_text_color"),
                )
            else:
                botao.configure(
                    fg_color=NEUTRAL_NAVIGATION_COLOR,
                    hover_color=NEUTRAL_NAVIGATION_HOVER_COLOR,
                )
        acao()
