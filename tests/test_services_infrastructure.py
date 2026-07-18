"""Testes da infraestrutura inicial da camada de serviços."""

from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from typing import get_args
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from models import Objeto, Relacao, Tag
from persistence import Database
from services import BaseService, DomainModel


class BaseServiceTests(unittest.TestCase):
    def test_preserva_a_instancia_de_persistencia_injetada(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            database = Database(Path(temporary_directory) / "banco.db")

            service = BaseService(database)

            self.assertIs(service.database, database)


class DomainModelTests(unittest.TestCase):
    def test_reune_os_modelos_de_dominio_existentes(self) -> None:
        self.assertEqual(set(get_args(DomainModel)), {Objeto, Tag, Relacao})
