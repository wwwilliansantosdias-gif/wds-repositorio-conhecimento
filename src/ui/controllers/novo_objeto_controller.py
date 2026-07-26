"""Controller do menu "Novo Objeto".

Une as quatro formas de criacao ja suportadas pelos Services
(importar_pdf, importar_markdown, cadastrar_link, criar_nota_manual)
em uma unica interface para a view, traduzindo os diferentes tipos de
excecao de cada caminho (DuplicataError, FileNotFoundError, ValueError,
falhas de extracao de texto) em um resultado uniforme.

A view do menu "Novo Objeto" nunca precisa saber qual excecao cada
Service pode levantar -- so trata sucesso ou mensagem_erro.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from models import Objeto
from services.importacao_service import DuplicataError, ImportacaoService


@dataclass
class ResultadoCriacao:
    """Resultado uniforme de qualquer uma das quatro formas de criar um objeto."""

    sucesso: bool
    objeto: Objeto | None = None
    mensagem_erro: str | None = None


class NovoObjetoController:
    """Controller acionado pelo botao "Novo Objeto" da Barra Superior."""

    def __init__(self, importacao_service: ImportacaoService) -> None:
        self._importacao_service = importacao_service

    def importar_pdf(
        self,
        caminho_arquivo: str | Path,
        *,
        titulo: str | None = None,
    ) -> ResultadoCriacao:
        """Importa um PDF e converte falhas em um resultado uniforme."""
        try:
            objeto = self._importacao_service.importar_pdf(
                caminho_arquivo, titulo=titulo
            )
            return ResultadoCriacao(sucesso=True, objeto=objeto)
        except DuplicataError as erro:
            return ResultadoCriacao(sucesso=False, mensagem_erro=str(erro))
        except FileNotFoundError:
            return ResultadoCriacao(
                sucesso=False, mensagem_erro="Arquivo nao encontrado."
            )
        except Exception as erro:
            return ResultadoCriacao(
                sucesso=False,
                mensagem_erro=f"Nao foi possivel importar o PDF: {erro}",
            )

    def importar_markdown(
        self,
        caminho_arquivo: str | Path,
        *,
        titulo: str | None = None,
    ) -> ResultadoCriacao:
        """Importa um arquivo Markdown e retorna seu resultado uniforme."""
        try:
            objeto = self._importacao_service.importar_markdown(
                caminho_arquivo, titulo=titulo
            )
            return ResultadoCriacao(sucesso=True, objeto=objeto)
        except DuplicataError as erro:
            return ResultadoCriacao(sucesso=False, mensagem_erro=str(erro))
        except FileNotFoundError:
            return ResultadoCriacao(
                sucesso=False, mensagem_erro="Arquivo nao encontrado."
            )
        except Exception as erro:
            return ResultadoCriacao(
                sucesso=False,
                mensagem_erro=f"Nao foi possivel importar o Markdown: {erro}",
            )

    def cadastrar_link(
        self,
        url: str,
        *,
        titulo: str | None = None,
    ) -> ResultadoCriacao:
        """Cadastra um link e converte falhas em um resultado uniforme."""
        try:
            objeto = self._importacao_service.cadastrar_link(url, titulo=titulo)
            return ResultadoCriacao(sucesso=True, objeto=objeto)
        except DuplicataError as erro:
            return ResultadoCriacao(sucesso=False, mensagem_erro=str(erro))
        except ValueError as erro:
            return ResultadoCriacao(sucesso=False, mensagem_erro=str(erro))
        except Exception as erro:
            return ResultadoCriacao(
                sucesso=False,
                mensagem_erro=f"Nao foi possivel cadastrar o link: {erro}",
            )

    def criar_nota(self, titulo: str) -> ResultadoCriacao:
        """Cria uma nota em branco, pronta para ser aberta no Editor
        Markdown. O conteudo e digitado depois, na propria tela do
        editor -- este metodo nao recebe texto inicial.
        """
        try:
            objeto = self._importacao_service.criar_nota_manual(titulo, conteudo="")
            return ResultadoCriacao(sucesso=True, objeto=objeto)
        except ValueError as erro:
            return ResultadoCriacao(sucesso=False, mensagem_erro=str(erro))
        except Exception as erro:
            return ResultadoCriacao(
                sucesso=False,
                mensagem_erro=f"Nao foi possivel criar a nota: {erro}",
            )
