"""Camada de orquestracao que mantem a busca sincronizada com o Acervo.

Este servico nao substitui ObjetoService nem EmbeddingService -- ele os
compoe, garantindo que toda escrita em objetos tambem atualize o indice
de busca semantica, sem exigir que quem usa o sistema lembre de indexar
manualmente (o problema que o Incremento 5.3 do Roadmap resolve).

ObjetoService e EmbeddingService continuam podendo ser usados
isoladamente (por exemplo, em testes ou scripts de manutencao). Este
servico e apenas o ponto de entrada recomendado para uso normal.
"""

from __future__ import annotations

from models import Objeto
from services.embedding_service import EmbeddingService
from services.objeto_service import ObjetoService


class AcervoService:
    """Ponto de entrada recomendado para cadastrar e manter o Acervo.

    Delega toda a persistencia para ObjetoService e toda a indexacao
    semantica para EmbeddingService, garantindo que as duas fiquem
    sempre consistentes entre si.
    """

    def __init__(
        self,
        objeto_service: ObjetoService,
        embedding_service: EmbeddingService,
    ) -> None:
        self._objeto_service = objeto_service
        self._embedding_service = embedding_service

    def cadastrar(
        self,
        titulo: str,
        tipo: str,
        *,
        caminho: str | None = None,
        resumo: str | None = None,
        hash_arquivo: str | None = None,
    ) -> Objeto:
        """Cadastra o objeto e o indexa imediatamente para busca semantica."""
        objeto = self._objeto_service.cadastrar(
            titulo,
            tipo,
            caminho=caminho,
            resumo=resumo,
            hash_arquivo=hash_arquivo,
        )
        self._embedding_service.indexar_objeto(objeto.id, objeto.titulo, objeto.resumo)
        return objeto

    def atualizar(self, objeto_id: int, titulo: str, tipo: str, **campos) -> Objeto:
        """Atualiza o objeto e reindexa com os dados mais recentes.

        Aceita os mesmos parametros de ObjetoService.atualizar,
        repassados sem alteracao -- este metodo nao precisa conhecer a
        lista exata de campos aceitos, apenas garante a reindexacao
        apos qualquer atualizacao.
        """
        objeto = self._objeto_service.atualizar(objeto_id, titulo, tipo, **campos)
        self._embedding_service.indexar_objeto(objeto.id, objeto.titulo, objeto.resumo)
        return objeto

    def excluir(self, objeto_id: int) -> Objeto:
        """Move o objeto para a lixeira (exclusao logica).

        O embedding permanece no indice do ChromaDB -- a busca semantica
        ja filtra por status = 'ativo' ao consultar o SQLite, exatamente
        como a busca textual via FTS5 ja faz. Nao ha necessidade de
        remover o vetor aqui.
        """
        return self._objeto_service.excluir(objeto_id)

    def restaurar(self, objeto_id: int) -> Objeto:
        """Restaura o objeto da lixeira.

        Como o embedding nunca foi removido durante a exclusao logica,
        a busca semantica volta a encontrar o objeto automaticamente
        assim que o status retorna a 'ativo'. Nenhuma reindexacao e
        necessaria.
        """
        return self._objeto_service.restaurar(objeto_id)

    def excluir_definitivamente(self, objeto_id: int) -> None:
        """Remove o objeto e seu embedding de forma definitiva.

        A exclusao em tabela_objetos (que ja remove tags e relacoes em
        cascade, conforme decidido na Fase 4) e a operacao autoritativa
        e acontece primeiro. A remocao do vetor no ChromaDB e feita na
        sequencia, em modo best-effort: se essa remocao falhar por
        qualquer motivo, a exclusao do objeto -- ja confirmada no
        SQLite -- nao e revertida. Um vetor orfao remanescente no
        ChromaDB nao causa dano, pois
        EmbeddingService.buscar_semantico ja ignora, de forma
        silenciosa, qualquer candidato cujo objeto nao exista mais no
        SQLite.
        """
        self._objeto_service.excluir_definitivamente(objeto_id)
        try:
            self._embedding_service.remover_do_indice(objeto_id)
        except Exception:
            pass

    # -- Metodos de leitura pura: delegam diretamente, sem logica extra --

    def obter_por_id(self, objeto_id: int) -> Objeto:
        return self._objeto_service.obter_por_id(objeto_id)

    def listar(self) -> list[Objeto]:
        return self._objeto_service.listar()

    def listar_ativos(self) -> list[Objeto]:
        return self._objeto_service.listar_ativos()

    def listar_lixeira(self) -> list[Objeto]:
        return self._objeto_service.listar_lixeira()