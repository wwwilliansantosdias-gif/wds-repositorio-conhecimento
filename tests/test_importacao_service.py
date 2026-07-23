"""Testes da fundacao do Servico de Importacao (Fase 6)."""

from __future__ import annotations

import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile, TemporaryDirectory
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from persistence import Database
from services.importacao_service import ImportacaoService, DuplicataError
from services.objeto_service import ObjetoService


class ImportacaoServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        temporary_path = Path(self.temporary_directory.name)
        
        self.database = Database(temporary_path / "banco.db")
        self.database.initialize()
        
        self.objeto_service = ObjetoService(self.database)
        self.importacao_service = ImportacaoService(self.objeto_service)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_calcular_hash_gera_sha256_correto_para_arquivo(self) -> None:
        conteudo = b"Conteudo de teste para hash"
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(conteudo)
            temp_path = temp_file.name

        try:
            hash_gerado = self.importacao_service.calcular_hash(temp_path)
            # O sha256 de "Conteudo de teste para hash"
            self.assertEqual(
            hash_gerado,
            "a1dd6544a87445346439572db643b9e95683a40565bb661026b369aaa44bf101"
        )
        finally:
            os.remove(temp_path)

    def test_verificar_duplicata_lanca_excecao_se_hash_ja_existir(self) -> None:
        hash_teste = "hash-duplicado-123"
        self.objeto_service.cadastrar(
            "Arquivo Existente", 
            "PDF", 
            hash_arquivo=hash_teste
        )

        with self.assertRaises(DuplicataError):
            self.importacao_service.verificar_duplicata(hash_teste)

    def test_verificar_duplicata_passa_silenciosamente_se_hash_for_novo(self) -> None:
        hash_teste = "hash-novo-123"
        # Nao deve lancar excecao
        self.importacao_service.verificar_duplicata(hash_teste)


if __name__ == "__main__":
    unittest.main()