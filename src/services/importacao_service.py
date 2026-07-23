"""Servico responsavel pela importacao de arquivos para o Acervo.

Garante o calculo de hash para deteccao de duplicatas e a coordenacao
do processamento de extracao de textos e arquivos fisicos.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from services.objeto_service import ObjetoService


class DuplicataError(Exception):
    """Excecao lancada quando um arquivo ja existe no acervo."""
    pass


class ImportacaoService:
    def __init__(self, objeto_service: ObjetoService) -> None:
        self._objeto_service = objeto_service

    def calcular_hash(self, caminho_arquivo: str | Path) -> str:
        """Calcula o hash SHA-256 do conteudo de um arquivo fisico."""
        caminho = Path(caminho_arquivo)
        if not caminho.is_file():
            raise FileNotFoundError(f"Arquivo nao encontrado: {caminho}")

        sha256 = hashlib.sha256()
        with open(caminho, "rb") as f:
            # Le em blocos para nao estourar a memoria com arquivos grandes
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        
        return sha256.hexdigest()

    def verificar_duplicata(self, hash_arquivo: str) -> None:
        """Verifica se um hash ja esta associado a um Objeto Ativo no acervo."""
        objetos = self._objeto_service.listar_ativos()
        for obj in objetos:
            if obj.hash_arquivo == hash_arquivo:
                raise DuplicataError(f"O arquivo ja esta no acervo (Objeto ID: {obj.id}).")