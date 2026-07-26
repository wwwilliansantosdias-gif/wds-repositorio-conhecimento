"""Controller da tela de Objeto em Foco e do painel de Contexto.

A view nunca chama AcervoService, TagService, RelacaoService ou
EmbeddingService diretamente -- sempre atraves deste controller,
conforme decidido em docs/interface-grafica.md.
"""

from __future__ import annotations

from dataclasses import dataclass

from models import Objeto, Relacao, Tag
from services.acervo_service import AcervoService
from services.embedding_service import EmbeddingService
from services.relacao_service import RelacaoService
from services.tag_service import TagService


@dataclass
class SugestaoSemantica:
    """Um item na secao 'Sugestoes Semanticas' do painel de Contexto.

    Possui score porque e resultado de uma comparacao de similaridade,
    diferente de um relacionamento explicito.
    """

    objeto: Objeto
    score: float


@dataclass
class DetalheObjeto:
    """Todo o conteudo necessario para renderizar a tela de Objeto em Foco."""

    objeto: Objeto
    tags: list[Tag]
    relacionamentos: list[Objeto]  # vinculos explicitos, sem score
    sugestoes: list[SugestaoSemantica]  # automaticas, com score


class ObjetoController:
    """Reune tudo que a view de Objeto em Foco precisa, vindo dos Services."""

    def __init__(
        self,
        acervo_service: AcervoService,
        tag_service: TagService,
        relacao_service: RelacaoService,
        embedding_service: EmbeddingService,
    ) -> None:
        self._acervo_service = acervo_service
        self._tag_service = tag_service
        self._relacao_service = relacao_service
        self._embedding_service = embedding_service

    def carregar_detalhe(
        self,
        objeto_id: int,
        limite_sugestoes: int = 5,
    ) -> DetalheObjeto:
        """Monta o conteudo completo da tela para um objeto especifico.

        Levanta LookupError (via AcervoService/ObjetoService) se
        objeto_id nao existir; a View decide como apresentar esse caso.
        """
        objeto = self._acervo_service.obter_por_id(objeto_id)
        tags = self._tag_service.listar_por_objeto(objeto_id)

        relacoes = self._relacao_service.listar_por_objeto(objeto_id)
        relacionamentos = self._resolver_objetos_relacionados(objeto_id, relacoes)

        sugestoes_brutas = self._embedding_service.buscar_similares_a_objeto(
            objeto_id, limite=limite_sugestoes
        )
        sugestoes = [
            SugestaoSemantica(objeto=obj, score=score)
            for obj, score in sugestoes_brutas
        ]

        return DetalheObjeto(
            objeto=objeto,
            tags=tags,
            relacionamentos=relacionamentos,
            sugestoes=sugestoes,
        )

    def _resolver_objetos_relacionados(
        self,
        objeto_id: int,
        relacoes: list[Relacao],
    ) -> list[Objeto]:
        """Traduz cada Relacao (que guarda apenas IDs) no Objeto do outro
        lado do vinculo -- nunca o proprio objeto em foco.

        Relacoes apontando para um objeto que nao existe mais (excluido
        definitivamente) sao ignoradas silenciosamente, ao inves de
        quebrar o carregamento da tela inteira.
        """
        objetos: list[Objeto] = []
        for relacao in relacoes:
            outro_id = (
                relacao.destino if relacao.origem == objeto_id else relacao.origem
            )
            try:
                objetos.append(self._acervo_service.obter_por_id(outro_id))
            except LookupError:
                continue
        return objetos
