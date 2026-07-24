"""Controller da tela de Pesquisa.

A view nunca chama PesquisaService ou EmbeddingService diretamente --
sempre atraves deste controller, conforme decidido em
docs/interface-grafica.md.
"""

from __future__ import annotations

from dataclasses import dataclass

from models import Objeto
from services.embedding_service import EmbeddingService
from services.pesquisa_service import PesquisaService


@dataclass
class ResultadoPesquisa:
    """Um item na lista de resultados da tela de Pesquisa."""

    objeto: Objeto
    score: float | None  # None quando encontrado apenas pela busca textual


class PesquisaController:
    """Combina busca textual (FTS5) e semantica (ChromaDB) em uma unica
    lista ordenada.

    Decisao de design (nao documentada anteriormente, resolvida aqui):
    resultados semanticos aparecem primeiro, ordenados por score
    decrescente, pois possuem uma medida explicita de relevancia.
    Resultados encontrados apenas pela busca textual aparecem em
    seguida, sem score, na ordem devolvida pelo FTS5. Um objeto
    encontrado pelos dois mecanismos aparece uma unica vez na lista,
    com o score da busca semantica.

    Esta decisao deve ser registrada em docs/interface-grafica.md
    quando a tela de Pesquisa for implementada.
    """

    def __init__(
        self,
        pesquisa_service: PesquisaService,
        embedding_service: EmbeddingService,
    ) -> None:
        self._pesquisa_service = pesquisa_service
        self._embedding_service = embedding_service

    def pesquisar(
        self,
        termo: str,
        limite_semantico: int = 10,
    ) -> list[ResultadoPesquisa]:
        """Executa a busca combinada. Retorna lista vazia para termo vazio."""
        termo = termo.strip()
        if not termo:
            return []

        semanticos = self._embedding_service.buscar_semantico(
            termo, limite=limite_semantico
        )
        ids_semanticos = {objeto.id for objeto, _ in semanticos}

        textuais = self._pesquisa_service.buscar_texto(termo)

        resultados = [
            ResultadoPesquisa(objeto=objeto, score=score)
            for objeto, score in semanticos
        ]
        for objeto in textuais:
            if objeto.id not in ids_semanticos:
                resultados.append(ResultadoPesquisa(objeto=objeto, score=None))

        return resultados
