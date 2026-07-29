"""Controller da tela de Backup.

Une o BackupService a uma interface simples para a view, seguindo o
mesmo padrao ja usado por LixeiraController: a view nunca chama o
Service diretamente, e nunca precisa saber quais excecoes cada
operacao pode levantar.
"""

from __future__ import annotations

from pathlib import Path

from services.backup_service import (
    BackupService,
    ResultadoBackup,
    ResultadoRestauracao,
    ResultadoValidacao,
)


class BackupController:
    """Controller da tela de Backup."""

    def __init__(self, backup_service: BackupService) -> None:
        self._backup_service = backup_service

    def listar_backups(self) -> list[Path]:
        """Retorna os backups existentes, do mais recente para o mais antigo."""
        return self._backup_service.listar_backups()

    def criar_backup(self) -> ResultadoBackup:
        """Cria um novo backup completo (banco.db + acervo/ + vetores/)."""
        return self._backup_service.criar_backup()

    def restaurar_backup(self, caminho_backup: Path | str) -> ResultadoRestauracao:
        """Restaura um backup existente, apos validar sua integridade.

        A troca de arquivos so acontece se o backup contiver os tres
        componentes obrigatorios -- restaurar_backup() no Service ja
        recusa um backup incompleto antes de tocar em qualquer arquivo
        atual.
        """
        return self._backup_service.restaurar_backup(caminho_backup)

    def validar_integridade(self, caminho_backup: Path | str) -> ResultadoValidacao:
        """Verifica se um backup esta completo, sem restaura-lo."""
        return self._backup_service.validar_integridade(caminho_backup)
