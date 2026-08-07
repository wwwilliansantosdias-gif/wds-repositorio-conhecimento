"""Miniatura de uma imagem no painel de Objeto em Foco.

Usado apenas para objetos do tipo "Imagem" -- carrega o arquivo fisico
referenciado por Objeto.caminho e exibe uma miniatura redimensionada,
preservando a proporcao original (nunca distorce). Se o arquivo nao
existir mais ou nao puder ser aberto como imagem, mostra uma mensagem
no lugar da miniatura em vez de quebrar a tela, mesmo padrao de estado
degradado ja usado em outros pontos da interface.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import customtkinter as ctk
from PIL import Image, UnidentifiedImageError

TAMANHO_MAXIMO = (440, 320)


def carregar_miniatura(caminho_arquivo: str | None) -> Image.Image | None:
    """Abre e redimensiona a imagem para caber em TAMANHO_MAXIMO.

    Retorna None quando o caminho e None, o arquivo nao existe, ou nao
    pode ser aberto como imagem -- nunca levanta excecao, para que o
    widget decida como representar essa indisponibilidade na tela.
    Separado da construcao do widget para poder ser testado sem
    depender de uma instancia real do Tkinter.
    """
    if caminho_arquivo is None or not Path(caminho_arquivo).is_file():
        return None

    try:
        with Image.open(caminho_arquivo) as arquivo_imagem:
            imagem = arquivo_imagem.copy()
    except (OSError, UnidentifiedImageError):
        return None

    imagem.thumbnail(TAMANHO_MAXIMO)
    return imagem


class MiniaturaImagem(ctk.CTkFrame):
    """Exibe a miniatura de um arquivo de imagem."""

    def __init__(
        self,
        master: Any,
        caminho_arquivo: str | None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        # Mantem a referencia viva: sem isso o Tkinter descarta a imagem
        # assim que o construtor termina e a miniatura aparece em branco.
        self._imagem_ctk: ctk.CTkImage | None = None

        imagem = carregar_miniatura(caminho_arquivo)
        if imagem is None:
            self._mostrar_indisponivel()
            return

        self._imagem_ctk = ctk.CTkImage(
            light_image=imagem, dark_image=imagem, size=imagem.size
        )
        ctk.CTkLabel(self, text="", image=self._imagem_ctk).grid(
            row=0, column=0, sticky="w"
        )

    def _mostrar_indisponivel(self) -> None:
        ctk.CTkLabel(
            self,
            text="Nao foi possivel carregar a miniatura desta imagem.",
            text_color="gray60",
        ).grid(row=0, column=0, sticky="w")
