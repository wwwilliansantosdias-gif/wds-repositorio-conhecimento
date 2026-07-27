"""Janela principal do WDS.

Monta a estrutura definida em docs/interface-grafica.md: Barra
Superior (com pesquisa), Resultados e Objeto em Foco + Contexto.

Instancia o banco de dados e todos os Services e Controllers aqui, e
os injeta nas views -- nenhuma view acessa um Service diretamente.
"""

from __future__ import annotations

import sys
from pathlib import Path

UI_DIRECTORY = Path(__file__).resolve().parent
SOURCE_DIRECTORY = UI_DIRECTORY.parent
for caminho in (SOURCE_DIRECTORY, UI_DIRECTORY):
    if str(caminho) not in sys.path:
        sys.path.insert(0, str(caminho))

import customtkinter as ctk

from persistence import Database
from services.acervo_service import AcervoService
from services.embedding_service import EmbeddingService
from services.importacao_service import ImportacaoService
from services.objeto_service import ObjetoService
from services.pesquisa_service import PesquisaService
from services.relacao_service import RelacaoService
from services.tag_service import TagService

from controllers.editor_markdown_controller import EditorMarkdownController
from controllers.lixeira_controller import LixeiraController
from controllers.novo_objeto_controller import NovoObjetoController
from controllers.objeto_controller import ObjetoController
from controllers.pesquisa_controller import PesquisaController
from controllers.tag_controller import TagController

from views.objeto import ObjetoView
from views.pesquisa import PesquisaView
from views.lixeira import LixeiraWindow
from widgets.novo_objeto_menu import NovoObjetoMenu
from widgets.toolbar import Toolbar


class MainWindow(ctk.CTk):
    """Janela principal que compõe os elementos da interface do WDS."""

    def __init__(self) -> None:
        super().__init__()
        self.title("WDS - Acervo de Conhecimento")
        self.geometry("1100x700")

        self._montar_servicos()
        self._montar_controllers()
        self._montar_layout()

    def _montar_servicos(self) -> None:
        self.database = Database()
        self.database.initialize()

        self.objeto_service = ObjetoService(self.database)
        self.tag_service = TagService(self.database)
        self.relacao_service = RelacaoService(self.database)
        self.pesquisa_service = PesquisaService(self.database)
        self.embedding_service = EmbeddingService(self.database)
        self.acervo_service = AcervoService(
            self.objeto_service, self.embedding_service
        )
        self.importacao_service = ImportacaoService(self.acervo_service)

    def _montar_controllers(self) -> None:
        self.pesquisa_controller = PesquisaController(
            self.pesquisa_service, self.embedding_service
        )
        self.tag_controller = TagController(self.tag_service, self.objeto_service)
        self.objeto_controller = ObjetoController(
            self.acervo_service,
            self.tag_service,
            self.relacao_service,
            self.embedding_service,
        )
        self.novo_objeto_controller = NovoObjetoController(self.importacao_service)
        self.editor_markdown_controller = EditorMarkdownController(
            self.acervo_service
        )
        self.lixeira_controller = LixeiraController(self.acervo_service)

        self.novo_objeto_menu = NovoObjetoMenu(
            self,
            self.novo_objeto_controller,
            ao_criar_objeto=self._ao_criar_objeto,
        )

    def _montar_layout(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.toolbar = Toolbar(
            self,
            ao_pesquisar=self._ao_pesquisar,
            ao_clicar_novo_objeto=self._ao_clicar_novo_objeto,
            ao_clicar_lixeira=self._ao_clicar_lixeira,
        )
        self.toolbar.grid(row=0, column=0, sticky="ew")

        corpo = ctk.CTkFrame(self, fg_color="transparent")
        corpo.grid(row=1, column=0, sticky="nsew")
        corpo.grid_rowconfigure(0, weight=1)
        corpo.grid_columnconfigure(0, weight=1, minsize=380)
        corpo.grid_columnconfigure(1, weight=2)

        self.pesquisa_view = PesquisaView(
            corpo,
            self.pesquisa_controller,
            self.tag_controller,
            ao_selecionar_objeto=self._ao_selecionar_objeto,
        )
        self.pesquisa_view.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=12)

        self.objeto_view = ObjetoView(
            corpo,
            self.objeto_controller,
            self.tag_controller,
            ao_selecionar_objeto=self._ao_selecionar_objeto,
            ao_selecionar_tag=self._ao_selecionar_tag,
        )
        self.objeto_view.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=12)

    def _ao_pesquisar(self, termo: str) -> None:
        self.pesquisa_view.pesquisar(termo)

    def _ao_selecionar_objeto(self, objeto_id: int) -> None:
        """Atualiza apenas o painel de Objeto em Foco -- os resultados
        da pesquisa a esquerda permanecem intactos."""
        self.objeto_view.mostrar_objeto(objeto_id)

    def _ao_selecionar_tag(self, nome_tag: str) -> None:
        """Atualiza os Resultados usando a pesquisa textual da tag."""
        self.pesquisa_view.pesquisar(nome_tag)

    def _ao_clicar_novo_objeto(self, x: int, y: int) -> None:
        self.novo_objeto_menu.abrir(x, y)

    def _ao_clicar_lixeira(self) -> None:
        LixeiraWindow(self, self.lixeira_controller)

    def _ao_criar_objeto(self, objeto_id: int) -> None:
        """Apos criar um objeto novo, mostra-o em Objeto em Foco.

        O item so aparecera na lista de Resultados quando o usuario
        pesquisar por ele -- a pesquisa continua sendo a ancora, o
        cadastro nao insere resultados fora desse fluxo.
        """
        self.objeto_view.mostrar_objeto(objeto_id)


def main() -> None:
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
