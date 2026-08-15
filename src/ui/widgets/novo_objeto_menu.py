"""Menu de criacao "Novo Objeto", acionado pelo botao na Barra Superior.

Oferece as formas de criacao suportadas por NovoObjetoController --
Importar Arquivo (PDF, Markdown, Docx, Planilha ou Imagem), Cadastrar
Link, Nova Nota -- conforme decidido em docs/interface-grafica.md e
docs/wds-1.1-planejamento.md. Cada opcao
coleta a entrada necessaria (seletor de arquivo nativo ou um
DialogoTexto) e delega ao controller, traduzindo o resultado em
feedback simples (mensagem de erro ou o novo objeto criado).

Toda chamada ao controller roda em segundo plano
(tarefas_segundo_plano.executar_em_segundo_plano) -- cadastrar um
objeto indexa seu vetor semantico, que envolve rodar o modelo de IA,
uma operacao lenta o bastante para travar a janela por um instante se
rodasse na thread principal.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Any

from controllers.novo_objeto_controller import NovoObjetoController, ResultadoCriacao
from tarefas_segundo_plano import executar_em_segundo_plano
from widgets.dialogo_texto import DialogoTexto


EXTENSOES_IMAGEM = frozenset({".png", ".jpg", ".jpeg"})
EXTENSOES_AUDIO = frozenset({".mp3", ".wav", ".m4a", ".ogg"})
EXTENSOES_VIDEO = frozenset({".mp4", ".mov", ".avi", ".mkv"})


class NovoObjetoMenu:
    """Controla o menu suspenso e os fluxos de criacao de objetos."""

    def __init__(
        self,
        master: Any,
        novo_objeto_controller: NovoObjetoController,
        ao_criar_objeto: Callable[[int], None],
        ao_criar_nota: Callable[[int], None],
    ) -> None:
        self._master = master
        self._controller = novo_objeto_controller
        self._ao_criar_objeto = ao_criar_objeto
        self._ao_criar_nota = ao_criar_nota

        self._menu = tk.Menu(master, tearoff=0)
        self._menu.add_command(label="Importar arquivo", command=self._importar_arquivo)
        self._menu.add_command(label="Cadastrar Link", command=self._cadastrar_link)
        self._menu.add_command(label="Nova Nota", command=self._nova_nota)

    def abrir(self, x: int, y: int) -> None:
        """Exibe o menu na posicao indicada (coordenadas de tela)."""
        try:
            self._menu.tk_popup(x, y)
        finally:
            self._menu.grab_release()

    def _importar_arquivo(self) -> None:
        caminho = filedialog.askopenfilename(
            title="Selecionar arquivo",
            filetypes=[
                (
                    "Arquivos suportados",
                    "*.pdf *.md *.docx *.xlsx *.png *.jpg *.jpeg "
                    "*.mp3 *.wav *.m4a *.ogg *.mp4 *.mov *.avi *.mkv",
                ),
                ("PDF", "*.pdf"),
                ("Markdown", "*.md"),
                ("Word", "*.docx"),
                ("Excel", "*.xlsx"),
                ("Imagem", "*.png *.jpg *.jpeg"),
                ("Audio", "*.mp3 *.wav *.m4a *.ogg"),
                ("Video", "*.mp4 *.mov *.avi *.mkv"),
            ],
        )
        if not caminho:
            return

        extensao = Path(caminho).suffix.lower()
        if extensao in EXTENSOES_IMAGEM:
            self._importar_imagem(caminho)
            return
        if extensao in EXTENSOES_AUDIO:
            self._importar_midia(caminho, "Audio", self._controller.importar_audio)
            return
        if extensao in EXTENSOES_VIDEO:
            self._importar_midia(caminho, "Video", self._controller.importar_video)
            return

        importadores = {
            ".pdf": self._controller.importar_pdf,
            ".md": self._controller.importar_markdown,
            ".docx": self._controller.importar_docx,
            ".xlsx": self._controller.importar_planilha,
        }
        importar = importadores.get(extensao)
        if importar is None:
            messagebox.showerror(
                "Formato nao suportado",
                "Selecione um arquivo PDF, Markdown, DOCX, XLSX, imagem, audio ou video.",
            )
            return
        self._executar(lambda: importar(caminho))

    def _importar_imagem(self, caminho: str) -> None:
        """Imagem exige um passo extra: sem OCR, o texto pesquisavel vem
        inteiramente da descricao digitada aqui -- mesmo padrao de
        DialogoTexto ja usado em _cadastrar_link()."""
        dialogo = DialogoTexto(
            self._master, "Importar Imagem", ["Titulo (opcional)", "Descricao"]
        )
        dados = dialogo.aguardar_resultado()
        if dados is None:
            return
        titulo = dados["Titulo (opcional)"].strip() or None
        descricao = dados["Descricao"].strip() or None
        self._executar(
            lambda: self._controller.importar_imagem(
                caminho, titulo=titulo, descricao=descricao
            )
        )

    def _importar_midia(
        self,
        caminho: str,
        tipo: str,
        importar: Callable[..., ResultadoCriacao],
    ) -> None:
        """Solicita titulo e descricao de audio ou video."""
        dialogo = DialogoTexto(
            self._master, f"Importar {tipo}", ["Titulo (opcional)", "Descricao"]
        )
        dados = dialogo.aguardar_resultado()
        if dados is None:
            return
        titulo = dados["Titulo (opcional)"].strip() or None
        descricao = dados["Descricao"].strip() or None
        self._executar(lambda: importar(caminho, titulo=titulo, descricao=descricao))

    def _cadastrar_link(self) -> None:
        dialogo = DialogoTexto(
            self._master, "Cadastrar Link", ["URL", "Titulo (opcional)"]
        )
        dados = dialogo.aguardar_resultado()
        if dados is None:
            return
        titulo = dados["Titulo (opcional)"].strip() or None
        self._executar(
            lambda: self._controller.cadastrar_link(dados["URL"], titulo=titulo)
        )

    def _nova_nota(self) -> None:
        dialogo = DialogoTexto(self._master, "Nova Nota", ["Titulo"])
        dados = dialogo.aguardar_resultado()
        if dados is None:
            return
        self._executar(
            lambda: self._controller.criar_nota(dados["Titulo"]),
            ao_sucesso=self._ao_criar_nota,
        )

    def _executar(
        self,
        chamada_ao_controller: Callable[[], ResultadoCriacao],
        *,
        ao_sucesso: Callable[[int], None] | None = None,
    ) -> None:
        """Roda a chamada ao controller em segundo plano e trata o
        resultado de volta na thread principal quando terminar."""
        executar_em_segundo_plano(
            self._master,
            chamada_ao_controller,
            ao_concluir=lambda resultado: self._tratar_resultado(
                resultado, ao_sucesso or self._ao_criar_objeto
            ),
            ao_falhar=self._tratar_erro_inesperado,
        )

    def _tratar_resultado(
        self, resultado: ResultadoCriacao, ao_sucesso: Callable[[int], None]
    ) -> None:
        if resultado.sucesso:
            ao_sucesso(resultado.objeto.id)
        else:
            messagebox.showerror(
                "Nao foi possivel criar o objeto", resultado.mensagem_erro
            )

    def _tratar_erro_inesperado(self, erro: Exception) -> None:
        messagebox.showerror("Erro inesperado", str(erro))
