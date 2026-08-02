"""Testes da abertura do arquivo original no painel de objeto."""

from __future__ import annotations

from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import Mock, patch
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
UI_DIRECTORY = SOURCE_DIRECTORY / "ui"
for caminho in (SOURCE_DIRECTORY, UI_DIRECTORY):
    if str(caminho) not in sys.path:
        sys.path.insert(0, str(caminho))

from models import Objeto
from views.objeto_view import ObjetoView


class ObjetoViewTests(unittest.TestCase):
    def _criar_objeto(self, tipo: str, caminho: str) -> Objeto:
        return Objeto(
            id=1,
            titulo="Objeto de teste",
            tipo=tipo,
            caminho=caminho,
            resumo=None,
            hash_arquivo=None,
            status="ativo",
            data_criacao="2026-08-01T10:00:00+00:00",
            data_edicao="2026-08-01T10:00:00+00:00",
            data_exclusao=None,
        )

    def test_abre_link_no_navegador_padrao(self) -> None:
        objeto = self._criar_objeto("Link", "https://example.com")

        with patch("views.objeto_view.webbrowser.open") as abrir:
            ObjetoView._abrir_original(objeto)

        abrir.assert_called_once_with("https://example.com")

    def test_abre_arquivo_local_no_aplicativo_padrao(self) -> None:
        objeto = self._criar_objeto("PDF", r"C:\\acervo\\pdfs\\1.pdf")

        with patch("views.objeto_view.os.startfile", create=True) as abrir:
            ObjetoView._abrir_original(objeto)

        abrir.assert_called_once_with(r"C:\\acervo\\pdfs\\1.pdf")

    def test_informa_erro_ao_nao_conseguir_abrir_arquivo_local(self) -> None:
        objeto = self._criar_objeto("PDF", r"C:\\acervo\\pdfs\\1.pdf")

        with (
            patch(
                "views.objeto_view.os.startfile",
                side_effect=OSError("Arquivo nao encontrado"),
                create=True,
            ),
            patch("views.objeto_view.messagebox.showerror") as mostrar_erro,
        ):
            ObjetoView._abrir_original(objeto)

        mostrar_erro.assert_called_once_with(
            "Não foi possível abrir o original", "Arquivo nao encontrado"
        )

    def test_botao_editar_e_visivel_somente_para_tipos_editaveis(self) -> None:
        for tipo, deve_exibir in (("Nota", True), ("Markdown", True), ("PDF", False)):
            with self.subTest(tipo=tipo):
                botoes: list[Mock] = []
                callback = Mock()
                objeto = self._criar_objeto(tipo, r"C:\\acervo\\notas\\1.md")
                detalhe = SimpleNamespace(
                    objeto=objeto,
                    tags=[],
                    relacionamentos=[],
                    sugestoes=[],
                )
                view = object.__new__(ObjetoView)
                view._objeto_controller = Mock(carregar_detalhe=Mock(return_value=detalhe))
                view._ao_editar_objeto = callback
                view._renderizar_tags_e_entrada = Mock()
                view._renderizar_secao_contexto = Mock(side_effect=lambda linha, **kwargs: linha + 1)
                view.winfo_children = Mock(return_value=[])

                def criar_botao(*args: object, **kwargs: object) -> Mock:
                    botao = Mock()
                    botao.configuracao = kwargs
                    botoes.append(botao)
                    return botao

                with (
                    patch("views.objeto_view.ctk.CTkFrame", return_value=Mock()),
                    patch("views.objeto_view.ctk.CTkLabel", return_value=Mock()),
                    patch("views.objeto_view.ctk.CTkButton", side_effect=criar_botao),
                    patch("views.objeto_view.ctk.CTkFont"),
                ):
                    view.mostrar_objeto(42)

                botao_editar = next(
                    (
                        botao
                        for botao in botoes
                        if botao.configuracao["text"] == "Editar"
                    ),
                    None,
                )
                self.assertEqual(botao_editar is not None, deve_exibir)
                if botao_editar is not None:
                    botao_editar.configuracao["command"]()
                    callback.assert_called_once_with(42)

    def test_botao_abrir_original_e_visivel_exceto_para_nota(self) -> None:
        for tipo, deve_exibir in (
            ("Nota", False),
            ("Markdown", True),
            ("PDF", True),
            ("Link", True),
        ):
            with self.subTest(tipo=tipo):
                botoes: list[Mock] = []
                objeto = self._criar_objeto(tipo, r"C:\\acervo\\notas\\1.md")
                detalhe = SimpleNamespace(
                    objeto=objeto,
                    tags=[],
                    relacionamentos=[],
                    sugestoes=[],
                )
                view = object.__new__(ObjetoView)
                view._objeto_controller = Mock(
                    carregar_detalhe=Mock(return_value=detalhe)
                )
                view._ao_editar_objeto = Mock()
                view._renderizar_tags_e_entrada = Mock()
                view._renderizar_secao_contexto = Mock(
                    side_effect=lambda linha, **kwargs: linha + 1
                )
                view.winfo_children = Mock(return_value=[])

                def criar_botao(*args: object, **kwargs: object) -> Mock:
                    botao = Mock()
                    botao.configuracao = kwargs
                    botoes.append(botao)
                    return botao

                with (
                    patch("views.objeto_view.ctk.CTkFrame", return_value=Mock()),
                    patch("views.objeto_view.ctk.CTkLabel", return_value=Mock()),
                    patch("views.objeto_view.ctk.CTkButton", side_effect=criar_botao),
                    patch("views.objeto_view.ctk.CTkFont"),
                ):
                    view.mostrar_objeto(42)

                textos = [botao.configuracao["text"] for botao in botoes]
                self.assertEqual("Abrir Original" in textos, deve_exibir)


if __name__ == "__main__":
    unittest.main()
