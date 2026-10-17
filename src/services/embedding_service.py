"""Serviço de indexação e busca semântica com ChromaDB."""

from __future__ import annotations

from pathlib import Path
from threading import Lock, RLock
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import chromadb
    from chromadb.api.models.Collection import Collection
    from sentence_transformers import SentenceTransformer

from models import Objeto
from services.base import BaseService
from services.objeto_service import ObjetoService


DEFAULT_CHROMA_PATH = Path(__file__).resolve().parents[2] / "vetores"
COLLECTION_NAME = "objetos_conhecimento"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
_CANDIDATE_MULTIPLIER = 3

_model: "SentenceTransformer | None" = None
_model_lock = Lock()


class EmbeddingService(BaseService):
    """Mantém embeddings no ChromaDB e recupera objetos semanticamente."""

    def __init__(
        self,
        database,
        chroma_path: Path | str = DEFAULT_CHROMA_PATH,
    ) -> None:
        super().__init__(database)
        self.chroma_path = Path(chroma_path)
        import chromadb

        self._model = _obter_modelo()
        self._client = chromadb.PersistentClient(path=str(chroma_path))
        self._collection: Any = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
            embedding_function=None,
        )
        self._objeto_service = ObjetoService(database)

    def indexar_objeto(
        self,
        objeto_id: int,
        titulo: str,
        resumo: str | None,
    ) -> None:
        """Gera e grava ou atualiza o embedding de um objeto."""
        texto = titulo if resumo is None else f"{titulo}\n{resumo}"
        self._collection.upsert(
            ids=[str(objeto_id)],
            embeddings=[self._gerar_embedding(texto)],
            metadatas=[{"objeto_id": objeto_id}],
        )

    def remover_do_indice(self, objeto_id: int) -> None:
        """Remove o embedding associado ao identificador informado."""
        self._collection.delete(ids=[str(objeto_id)])

    def buscar_semantico(
        self,
        termo: str,
        limite: int = 10,
    ) -> list[tuple[Objeto, float]]:
        """Retorna objetos ativos ordenados por similaridade semântica."""
        if limite <= 0:
            return []

        quantidade_indexada = self._collection.count()
        if quantidade_indexada == 0:
            return []

        quantidade_candidatos = min(
            quantidade_indexada,
            limite * _CANDIDATE_MULTIPLIER,
        )
        resultado = self._collection.query(
            query_embeddings=[self._gerar_embedding(termo)],
            n_results=quantidade_candidatos,
            include=["distances"],
        )
        ids = resultado["ids"][0]
        distancias = resultado["distances"][0]

        encontrados: list[tuple[Objeto, float]] = []
        for identificador, distancia in zip(ids, distancias, strict=True):
            try:
                objeto = self._objeto_service.obter_por_id(int(identificador))
            except LookupError:
                # Um vetor residual não representa mais um objeto no SQLite.
                continue

            if objeto.status != "ativo":
                continue

            encontrados.append((objeto, _score_percentual(distancia)))

        encontrados.sort(key=lambda resultado: resultado[1], reverse=True)
        return encontrados[:limite]

    def buscar_similares_a_objeto(
        self,
        objeto_id: int,
        limite: int = 5,
    ) -> list[tuple[Objeto, float]]:
        """Retorna objetos ativos semanticamente parecidos com um objeto existente.

        Diferente de buscar_semantico (que parte de um texto de busca
        digitado pelo usuario), este metodo reaproveita o embedding ja
        armazenado para objeto_id -- nao gera um novo embedding, apenas
        reconsulta o vetor existente contra os demais indexados.

        O proprio objeto nunca aparece nos resultados. Usado para
        preencher a secao "Sugestoes semanticas" do painel de Contexto
        na interface, ao lado dos relacionamentos explicitos
        (RelacaoService), que nao possuem score.
        """
        if limite <= 0:
            return []

        registro = self._collection.get(
            ids=[str(objeto_id)],
            include=["embeddings"],
        )
        if len(registro["ids"]) == 0:
            return []
        vetor = registro["embeddings"][0]

        quantidade_indexada = self._collection.count()
        # +1 para compensar o proprio objeto, que sera excluido a seguir.
        quantidade_candidatos = min(
            quantidade_indexada,
            (limite + 1) * _CANDIDATE_MULTIPLIER,
        )
        resultado = self._collection.query(
            query_embeddings=[vetor],
            n_results=quantidade_candidatos,
            include=["distances"],
        )
        ids = resultado["ids"][0]
        distancias = resultado["distances"][0]

        encontrados: list[tuple[Objeto, float]] = []
        for identificador, distancia in zip(ids, distancias, strict=True):
            if int(identificador) == objeto_id:
                continue

            try:
                objeto = self._objeto_service.obter_por_id(int(identificador))
            except LookupError:
                continue

            if objeto.status != "ativo":
                continue

            encontrados.append((objeto, _score_percentual(distancia)))

        encontrados.sort(key=lambda resultado: resultado[1], reverse=True)
        return encontrados[:limite]

    def _gerar_embedding(self, texto: str) -> list[float]:
        return self._model.encode(texto).tolist()


def _obter_modelo() -> "SentenceTransformer":
    """Carrega o modelo uma vez por processo, pois a carga é custosa."""
    global _model

    with _model_lock:
        if _model is None:
            from sentence_transformers import SentenceTransformer

            _model = SentenceTransformer(MODEL_NAME)
        return _model


class LazyEmbeddingService:
    """Facade que deixa o acervo utilizavel enquanto a IA inicializa.

    Chamadas de escrita feitas antes da disponibilidade semantica ficam
    enfileiradas e sao reproduzidas na mesma ordem apos o servico real
    estar pronto. Consultas semanticas retornam vazio durante a carga;
    a busca textual continua independente no PesquisaService.
    """

    def __init__(self, database, chroma_path: Path | str = DEFAULT_CHROMA_PATH) -> None:
        self._database = database
        self._chroma_path = chroma_path
        self._servico: EmbeddingService | None = None
        self._erro: Exception | None = None
        self._pendentes: list[tuple[str, tuple, dict]] = []
        self._lock = RLock()

    @property
    def disponivel(self) -> bool:
        with self._lock:
            return self._servico is not None

    @property
    def erro(self) -> Exception | None:
        with self._lock:
            return self._erro

    def carregar(self) -> None:
        """Carrega o servico pesado; deve ser chamado fora da UI."""
        try:
            servico = EmbeddingService(self._database, self._chroma_path)
        except Exception as erro:  # noqa: BLE001 - exposto no indicador da UI
            with self._lock:
                self._erro = erro
            return

        with self._lock:
            self._servico = servico
            pendentes = self._pendentes
            self._pendentes = []

        for nome, args, kwargs in pendentes:
            getattr(servico, nome)(*args, **kwargs)

    def _encaminhar_ou_enfileirar(self, nome: str, *args, **kwargs) -> None:
        with self._lock:
            if self._servico is None:
                self._pendentes.append((nome, args, kwargs))
                return
            servico = self._servico
        getattr(servico, nome)(*args, **kwargs)

    def indexar_objeto(self, *args, **kwargs) -> None:
        self._encaminhar_ou_enfileirar("indexar_objeto", *args, **kwargs)

    def remover_do_indice(self, *args, **kwargs) -> None:
        self._encaminhar_ou_enfileirar("remover_do_indice", *args, **kwargs)

    def buscar_semantico(self, *args, **kwargs) -> list:
        with self._lock:
            servico = self._servico
        return [] if servico is None else servico.buscar_semantico(*args, **kwargs)

    def buscar_similares_a_objeto(self, *args, **kwargs) -> list:
        with self._lock:
            servico = self._servico
        return [] if servico is None else servico.buscar_similares_a_objeto(*args, **kwargs)


def _score_percentual(distancia: float) -> float:
    """Converte a distância cosseno do ChromaDB em similaridade percentual."""
    similaridade = 1 - distancia
    return round(max(0.0, min(1.0, similaridade)) * 100, 0)
