"""Controller da tela de Pesquisa.

A view nunca chama PesquisaService ou EmbeddingService diretamente --
sempre atraves deste controller, conforme decidido em
docs/interface-grafica.md.
"""

from __future__ import annotations

from dataclasses import dataclass

from models import Objeto
from services.acervo_service import AcervoService
from services.embedding_service import EmbeddingService
from services.pesquisa_service import PesquisaService


@dataclass
class ResultadoPesquisa:
    """Um item na lista de resultados da tela de Pesquisa."""

    objeto: Objeto
    score: float | None  # None quando encontrado apenas pela busca textual
    trecho: str | None = None


class PesquisaController:
    """Combina busca textual (FTS5) e semantica (ChromaDB) em uma unica
    lista ordenada.

    Decisao de design (nao documentada anteriormente, resolvida aqui):
    resultados textuais aparecem primeiro, na ordem devolvida pelo
    FTS5, pois um match exato tem prioridade sobre similaridade.
    Resultados semanticos aparecem em seguida, ordenados por score
    decrescente. Um objeto encontrado pelos dois mecanismos aparece
    uma unica vez como resultado textual, sem score.

    Esta decisao deve ser registrada em docs/interface-grafica.md
    quando a tela de Pesquisa for implementada.
    """

    def __init__(
        self,
        pesquisa_service: PesquisaService,
        embedding_service: EmbeddingService,
        acervo_service: AcervoService,
        limite_semantico_padrao: int = 10,
    ) -> None:
        self._pesquisa_service = pesquisa_service
        self._embedding_service = embedding_service
        self._acervo_service = acervo_service
        self._limite_semantico_padrao = limite_semantico_padrao

    def pesquisar(
        self,
        termo: str,
        limite_semantico: int | None = None,
    ) -> list[ResultadoPesquisa]:
        """Executa a busca combinada. Retorna lista vazia para termo vazio.

        limite_semantico, quando omitido, usa o valor configurado em
        Configuracoes (ConfigService.limite_resultados_semanticos) --
        passado ao construtor deste controller, nao lido novamente
        aqui a cada busca.
        """
        termo = termo.strip()
        if not termo:
            return []

        limite = (
            limite_semantico
            if limite_semantico is not None
            else self._limite_semantico_padrao
        )

        textuais = self._pesquisa_service.buscar_texto(termo)
        ids_textuais = {objeto.id for objeto, _ in textuais}
        semanticos = self._embedding_service.buscar_semantico(termo, limite=limite)

        resultados = [
            ResultadoPesquisa(objeto=objeto, score=None, trecho=trecho)
            for objeto, trecho in textuais
        ]
        resultados.extend(
            ResultadoPesquisa(objeto=objeto, score=score)
            for objeto, score in semanticos
            if objeto.id not in ids_textuais
        )

        return resultados

    @property
    def busca_semantica_disponivel(self) -> bool:
        """Indica se o facade semantico ja terminou seu carregamento."""
        return bool(getattr(self._embedding_service, "disponivel", True))

    def listar_todos(self) -> list[ResultadoPesquisa]:
        """Lista todos os objetos ativos do Acervo, sem nenhum termo de
        busca -- usado pela Biblioteca (docs/interface-grafica.md,
        "Apresenta todos os Objetos de Conhecimento. Utiliza os mesmos
        componentes da pesquisa").

        Sem termo de busca nao ha relevancia a medir, entao nenhum item
        recebe score (mesmo significado de score=None na busca textual:
        "nao ha uma medida de parecenca aqui"). Mostra o mais recente
        primeiro, mesma convencao ja usada na Lixeira.
        """
        objetos = self._acervo_service.listar_ativos()
        return [
            ResultadoPesquisa(objeto=objeto, score=None)
            for objeto in reversed(objetos)
        ]
