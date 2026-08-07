"""Controller de Tags.

Une criacao/reaproveitamento de tags e associacao a objetos em uma
unica operacao "adicionar tag".
"""

from __future__ import annotations

from dataclasses import dataclass

from models import Tag
from services.acervo_service import AcervoService
from services.objeto_service import ObjetoService
from services.tag_service import TagService


@dataclass
class ResultadoAdicionarTag:
    """Resultado uniforme de adicionar uma tag a um objeto."""

    sucesso: bool
    tag: Tag | None = None
    mensagem_erro: str | None = None


class TagController:
    """Controller usado pelo widget de tags na tela de Objeto em Foco."""

    def __init__(
        self,
        tag_service: TagService,
        objeto_service: ObjetoService,
        acervo_service: AcervoService,
    ) -> None:
        self._tag_service = tag_service
        self._objeto_service = objeto_service
        self._acervo_service = acervo_service

    def listar_todas(self) -> list[Tag]:
        """Retorna todas as tags do sistema, para sugestao/autocompletar."""
        return self._tag_service.listar()

    def listar_por_objeto(self, objeto_id: int) -> list[Tag]:
        """Retorna as tags atualmente associadas ao objeto informado."""
        return self._tag_service.listar_por_objeto(objeto_id)

    def adicionar_tag(self, objeto_id: int, nome_tag: str) -> ResultadoAdicionarTag:
        """Associa uma tag ao objeto, criando-a apenas se ainda nao existir.

        Decisao de UX (nao documentada anteriormente, resolvida aqui):
        se ja existir uma tag com o mesmo nome, ela e reaproveitada em
        vez de retornar erro de duplicata. Digitar o nome de uma tag ja
        existente deve associa-la ao objeto, nao bloquear a acao.

        A existencia do objeto e validada ANTES de criar ou reaproveitar
        qualquer tag: TagService nao possui metodo para excluir uma tag,
        entao criar a tag antes de validar o objeto deixaria uma tag
        orfa no sistema caso a associacao falhasse.
        """
        nome_tag = nome_tag.strip()
        if not nome_tag:
            return ResultadoAdicionarTag(
                sucesso=False, mensagem_erro="O nome da tag nao pode ser vazio."
            )

        try:
            self._objeto_service.obter_por_id(objeto_id)
        except LookupError as erro:
            return ResultadoAdicionarTag(sucesso=False, mensagem_erro=str(erro))

        tag = self._buscar_por_nome(nome_tag) or self._tag_service.criar(nome_tag)
        self._tag_service.associar(objeto_id, tag.id)
        self._reindexar_com_tags_atuais(objeto_id)
        return ResultadoAdicionarTag(sucesso=True, tag=tag)

    def remover_tag(self, objeto_id: int, tag_id: int) -> None:
        """Remove a associacao entre a tag e o objeto.

        A Tag em si permanece disponivel para outros objetos -- apenas
        o vinculo com este objeto especifico e removido.
        """
        self._tag_service.desassociar(objeto_id, tag_id)
        self._reindexar_com_tags_atuais(objeto_id)

    def _buscar_por_nome(self, nome: str) -> Tag | None:
        for tag in self._tag_service.listar():
            if tag.nome == nome:
                return tag
        return None

    def _reindexar_com_tags_atuais(self, objeto_id: int) -> None:
        """Reindexa o vetor semantico do objeto para refletir as tags
        atualmente associadas a ele.

        TagService so mexe no SQLite e nunca passa pelo AcervoService,
        entao associar/desassociar uma tag nunca atualizava o vetor
        semantico do objeto antes desta chamada. Usa
        AcervoService.reindexar_com_contexto_extra (nao `atualizar`)
        para nunca sujar o resumo persistido no SQLite com texto de
        tag. Lista de tags vazia (removeu a ultima) gera texto extra
        vazio, sem erro.

        Melhor esforco, mesmo padrao ja usado em
        AcervoService.excluir_definitivamente para a remocao do vetor:
        se a reindexacao falhar por qualquer motivo (objeto ja nao
        existe mais, EmbeddingService indisponivel etc.), a
        associacao/remocao da tag no SQLite -- ja confirmada -- nao e
        desfeita nem reportada como erro ao usuario.
        """
        tags_atuais = self._tag_service.listar_por_objeto(objeto_id)
        nomes_tags = ", ".join(tag.nome for tag in tags_atuais)
        texto_extra = f"Tags: {nomes_tags}" if nomes_tags else ""

        try:
            self._acervo_service.reindexar_com_contexto_extra(objeto_id, texto_extra)
        except Exception:
            pass
