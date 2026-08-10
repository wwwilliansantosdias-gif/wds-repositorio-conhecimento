"""Controller para criação de relacionamentos entre Objetos."""

from __future__ import annotations

from dataclasses import dataclass

from models import Objeto, Relacao
from services.pesquisa_service import PesquisaService
from services.relacao_service import RelacaoService

from controllers.novo_objeto_controller import NovoObjetoController


@dataclass
class ResultadoCriarRelacionamento:
    """Resultado uniforme da criação de um relacionamento."""

    sucesso: bool
    relacao: Relacao | None = None
    mensagem_erro: str | None = None


class RelacaoController:
    """Orquestra a busca e criação de relacionamentos para a interface."""

    def __init__(
        self,
        relacao_service: RelacaoService,
        pesquisa_service: PesquisaService,
        novo_objeto_controller: NovoObjetoController,
    ) -> None:
        self._relacao_service = relacao_service
        self._pesquisa_service = pesquisa_service
        self._novo_objeto_controller = novo_objeto_controller

    def buscar_objetos_para_relacionar(
        self, termo: str, excluir_id: int
    ) -> list[Objeto]:
        """Busca objetos textualmente, excluindo o objeto em foco."""
        resultados = self._pesquisa_service.buscar_texto(termo)
        return [objeto for objeto, _trecho in resultados if objeto.id != excluir_id]

    def listar_tipos_usados(self) -> list[str]:
        """Retorna os tipos de relação disponíveis como sugestões."""
        return self._relacao_service.listar_tipos_distintos()

    def criar(
        self, origem_id: int, destino_id: int, tipo_relacao: str
    ) -> ResultadoCriarRelacionamento:
        """Cria uma relação e converte erros esperados em resultado."""
        tipo_relacao = tipo_relacao.strip()
        if not tipo_relacao:
            return ResultadoCriarRelacionamento(
                sucesso=False,
                mensagem_erro="O tipo da relação não pode ser vazio.",
            )

        try:
            relacao = self._relacao_service.criar(
                origem_id, destino_id, tipo_relacao
            )
        except (LookupError, ValueError) as erro:
            return ResultadoCriarRelacionamento(
                sucesso=False, mensagem_erro=str(erro)
            )

        return ResultadoCriarRelacionamento(sucesso=True, relacao=relacao)

    def criar_objeto_e_relacionar(
        self, origem_id: int, titulo_novo_objeto: str, tipo_relacao: str
    ) -> ResultadoCriarRelacionamento:
        """Cria uma Nota em branco e a relaciona ao objeto de origem."""
        resultado_criacao = self._novo_objeto_controller.criar_nota(
            titulo_novo_objeto
        )
        if not resultado_criacao.sucesso:
            return ResultadoCriarRelacionamento(
                sucesso=False, mensagem_erro=resultado_criacao.mensagem_erro
            )

        if resultado_criacao.objeto is None:
            return ResultadoCriarRelacionamento(
                sucesso=False,
                mensagem_erro="Não foi possível criar a nota para o relacionamento.",
            )

        return self.criar(origem_id, resultado_criacao.objeto.id, tipo_relacao)
