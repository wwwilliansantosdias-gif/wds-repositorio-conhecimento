"""Controller da tela de Lixeira.

Lista objetos excluidos logicamente e permite restaura-los ou
exclui-los definitivamente, conforme decidido em
docs/interface-grafica.md (tela incluida no MVP, nao adiada).
"""

from __future__ import annotations

from dataclasses import dataclass

from models import Objeto
from services.acervo_service import AcervoService


@dataclass
class ResultadoAcaoLixeira:
    """Resultado uniforme de restaurar ou excluir definitivamente."""

    sucesso: bool
    objeto: Objeto | None = None
    mensagem_erro: str | None = None


class LixeiraController:
    """Controller da tela de Lixeira."""

    def __init__(self, acervo_service: AcervoService) -> None:
        self._acervo_service = acervo_service

    def listar(self) -> list[Objeto]:
        """Retorna todos os objetos atualmente na lixeira."""
        return self._acervo_service.listar_lixeira()

    def restaurar(self, objeto_id: int) -> ResultadoAcaoLixeira:
        """Restaura um objeto da lixeira, tornando-o ativo novamente."""
        try:
            objeto = self._acervo_service.restaurar(objeto_id)
            return ResultadoAcaoLixeira(sucesso=True, objeto=objeto)
        except LookupError as erro:
            return ResultadoAcaoLixeira(sucesso=False, mensagem_erro=str(erro))

    def excluir_definitivamente(self, objeto_id: int) -> ResultadoAcaoLixeira:
        """Remove o objeto e seus vinculos de forma definitiva e irreversivel.

        So pode ser chamado em um objeto que ja esteja na lixeira --
        ObjetoService recusa a exclusao definitiva de um objeto ativo,
        e esse caso e traduzido aqui em um resultado tratado, nao uma
        excecao crua.
        """
        try:
            self._acervo_service.excluir_definitivamente(objeto_id)
            return ResultadoAcaoLixeira(sucesso=True)
        except LookupError as erro:
            return ResultadoAcaoLixeira(sucesso=False, mensagem_erro=str(erro))
        except ValueError as erro:
            return ResultadoAcaoLixeira(sucesso=False, mensagem_erro=str(erro))
