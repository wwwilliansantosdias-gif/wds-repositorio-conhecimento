"""Controller do Editor Markdown.

Carrega e salva o conteudo de Notas (tipo "Nota" ou "Markdown"), que
sempre correspondem a um arquivo fisico real em acervo/notas/{id}.md,
conforme decidido em docs/interface-grafica.md.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from models import Objeto
from services.acervo_service import AcervoService


TIPOS_EDITAVEIS = frozenset({"Nota", "Markdown"})


@dataclass
class ConteudoNota:
    """Conteudo carregado de uma Nota, pronto para exibir no editor."""

    objeto: Objeto
    texto: str


@dataclass
class ResultadoSalvar:
    """Resultado uniforme de uma tentativa de salvar a edicao."""

    sucesso: bool
    objeto: Objeto | None = None
    mensagem_erro: str | None = None


class EditorMarkdownController:
    """Controller da tela de Editor Markdown."""

    def __init__(self, acervo_service: AcervoService) -> None:
        self._acervo_service = acervo_service

    def carregar(self, objeto_id: int) -> ConteudoNota:
        """Carrega o conteudo fisico de uma Nota para edicao.

        Levanta LookupError se o objeto nao existir, e ValueError se o
        objeto nao for do tipo Nota/Markdown ou nao possuir arquivo
        fisico associado -- ambos casos que a view deve tratar sem
        deixar a tela quebrar.
        """
        objeto = self._acervo_service.obter_por_id(objeto_id)

        if objeto.tipo not in TIPOS_EDITAVEIS:
            raise ValueError(
                f"O Editor Markdown nao edita objetos do tipo '{objeto.tipo}'."
            )
        if objeto.caminho is None:
            raise ValueError(
                f"Objeto {objeto_id} nao possui arquivo fisico associado."
            )

        texto = Path(objeto.caminho).read_text(encoding="utf-8")
        return ConteudoNota(objeto=objeto, texto=texto)

    def salvar(self, objeto_id: int, novo_texto: str) -> ResultadoSalvar:
        """Salva o conteudo editado, atualizando o arquivo fisico e
        reindexando o objeto para busca textual e semantica.

        A escrita em disco e atomica: grava em um arquivo temporario e
        so substitui o original apos a gravacao ser concluida com
        sucesso, para nunca corromper a nota caso o processo seja
        interrompido no meio da escrita.
        """
        try:
            objeto = self._acervo_service.obter_por_id(objeto_id)
        except LookupError as erro:
            return ResultadoSalvar(sucesso=False, mensagem_erro=str(erro))

        if objeto.tipo not in TIPOS_EDITAVEIS:
            return ResultadoSalvar(
                sucesso=False,
                mensagem_erro=(
                    f"O Editor Markdown nao edita objetos do tipo '{objeto.tipo}'."
                ),
            )
        if objeto.caminho is None:
            return ResultadoSalvar(
                sucesso=False,
                mensagem_erro=(
                    f"Objeto {objeto_id} nao possui arquivo fisico associado."
                ),
            )

        try:
            self._escrever_atomicamente(Path(objeto.caminho), novo_texto)
        except OSError as erro:
            return ResultadoSalvar(
                sucesso=False,
                mensagem_erro=f"Nao foi possivel salvar o arquivo: {erro}",
            )

        objeto_atualizado = self._acervo_service.atualizar(
            objeto_id,
            objeto.titulo,
            objeto.tipo,
            resumo=novo_texto,
        )
        return ResultadoSalvar(sucesso=True, objeto=objeto_atualizado)

    def _escrever_atomicamente(self, caminho: Path, texto: str) -> None:
        """Grava em um arquivo temporario no mesmo diretorio e substitui
        o arquivo original apenas apos a gravacao ser concluida."""
        caminho_temporario = caminho.with_suffix(caminho.suffix + ".tmp")
        caminho_temporario.write_text(texto, encoding="utf-8")
        os.replace(caminho_temporario, caminho)
