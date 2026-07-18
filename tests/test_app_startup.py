"""Testes de inicialização do ponto de entrada da aplicação."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ApplicationStartupTests(unittest.TestCase):
    def test_application_initialization_check_succeeds(self) -> None:
        result = subprocess.run(
            [sys.executable, "app.py", "--check"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

