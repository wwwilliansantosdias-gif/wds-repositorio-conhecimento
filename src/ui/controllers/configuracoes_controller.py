"""Controller da tela de Configuracoes."""

from __future__ import annotations

from services.config_service import Config, ConfigService, ResultadoSalvarConfig


class ConfiguracoesController:
    """Controller da tela de Configuracoes."""

    def __init__(self, config_service: ConfigService) -> None:
        self._config_service = config_service

    def carregar(self) -> Config:
        return self._config_service.carregar()

    def salvar(self, tema: str, limite_resultados_semanticos: int) -> ResultadoSalvarConfig:
        config = Config(
            tema=tema,
            limite_resultados_semanticos=limite_resultados_semanticos,
        )
        return self._config_service.salvar(config)
