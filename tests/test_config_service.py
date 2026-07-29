"""Testes do ConfigService -- carregar, salvar e validar config.json."""

from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from services.config_service import Config, ConfigService


class ConfigServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.caminho_config = Path(self.temporary_directory.name) / "config.json"
        self.service = ConfigService(self.caminho_config)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    # ---- carregar ---------------------------------------------------

    def test_carregar_sem_arquivo_retorna_defaults(self) -> None:
        config = self.service.carregar()

        self.assertEqual(config.tema, "Sistema")
        self.assertEqual(config.limite_resultados_semanticos, 10)

    def test_carregar_arquivo_corrompido_retorna_defaults_sem_lancar_excecao(
        self,
    ) -> None:
        self.caminho_config.write_text("isso nao e json valido {{{", encoding="utf-8")

        config = self.service.carregar()

        self.assertEqual(config.tema, "Sistema")
        self.assertEqual(config.limite_resultados_semanticos, 10)

    def test_carregar_arquivo_com_lista_em_vez_de_objeto_retorna_defaults(self) -> None:
        self.caminho_config.write_text("[1, 2, 3]", encoding="utf-8")

        config = self.service.carregar()

        self.assertEqual(config.tema, "Sistema")

    def test_carregar_tema_invalido_no_arquivo_cai_para_default(self) -> None:
        self.caminho_config.write_text(
            '{"tema": "Roxo Neon", "limite_resultados_semanticos": 15}',
            encoding="utf-8",
        )

        config = self.service.carregar()

        self.assertEqual(config.tema, "Sistema")
        self.assertEqual(config.limite_resultados_semanticos, 15)

    def test_carregar_limite_fora_do_intervalo_cai_para_default(self) -> None:
        self.caminho_config.write_text(
            '{"tema": "Escuro", "limite_resultados_semanticos": 999}',
            encoding="utf-8",
        )

        config = self.service.carregar()

        self.assertEqual(config.tema, "Escuro")
        self.assertEqual(config.limite_resultados_semanticos, 10)

    def test_carregar_limite_como_texto_em_vez_de_numero_cai_para_default(self) -> None:
        self.caminho_config.write_text(
            '{"limite_resultados_semanticos": "dez"}', encoding="utf-8"
        )

        config = self.service.carregar()

        self.assertEqual(config.limite_resultados_semanticos, 10)

    # ---- salvar -------------------------------------------------------

    def test_salvar_e_depois_carregar_recupera_os_mesmos_valores(self) -> None:
        resultado = self.service.salvar(Config(tema="Escuro", limite_resultados_semanticos=25))

        self.assertTrue(resultado.sucesso, resultado.mensagem_erro)

        config_recarregada = self.service.carregar()
        self.assertEqual(config_recarregada.tema, "Escuro")
        self.assertEqual(config_recarregada.limite_resultados_semanticos, 25)

    def test_salvar_sobrescreve_valores_anteriores_por_completo(self) -> None:
        self.service.salvar(Config(tema="Escuro", limite_resultados_semanticos=25))
        self.service.salvar(Config(tema="Claro", limite_resultados_semanticos=5))

        config_final = self.service.carregar()
        self.assertEqual(config_final.tema, "Claro")
        self.assertEqual(config_final.limite_resultados_semanticos, 5)

    def test_salvar_tema_invalido_retorna_erro_e_nao_grava_nada(self) -> None:
        resultado = self.service.salvar(
            Config(tema="Roxo Neon", limite_resultados_semanticos=10)
        )

        self.assertFalse(resultado.sucesso)
        self.assertIsNotNone(resultado.mensagem_erro)
        self.assertFalse(self.caminho_config.exists())

    def test_salvar_limite_abaixo_do_minimo_retorna_erro(self) -> None:
        resultado = self.service.salvar(
            Config(tema="Sistema", limite_resultados_semanticos=0)
        )

        self.assertFalse(resultado.sucesso)

    def test_salvar_limite_acima_do_maximo_retorna_erro(self) -> None:
        resultado = self.service.salvar(
            Config(tema="Sistema", limite_resultados_semanticos=51)
        )

        self.assertFalse(resultado.sucesso)

    def test_salvar_cria_pasta_pai_se_nao_existir(self) -> None:
        caminho_aninhado = (
            Path(self.temporary_directory.name) / "pasta_nova" / "config.json"
        )
        service = ConfigService(caminho_aninhado)

        resultado = service.salvar(Config(tema="Claro", limite_resultados_semanticos=8))

        self.assertTrue(resultado.sucesso, resultado.mensagem_erro)
        self.assertTrue(caminho_aninhado.is_file())

    # ---- tema_ctk -------------------------------------------------------

    def test_tema_ctk_mapeia_para_os_valores_esperados_pelo_customtkinter(self) -> None:
        self.assertEqual(Config(tema="Sistema").tema_ctk, "system")
        self.assertEqual(Config(tema="Claro").tema_ctk, "light")
        self.assertEqual(Config(tema="Escuro").tema_ctk, "dark")


if __name__ == "__main__":
    unittest.main()
