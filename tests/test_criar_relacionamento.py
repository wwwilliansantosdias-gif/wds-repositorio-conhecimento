"""Testes do widget inline de criação de relacionamentos."""

from __future__ import annotations

from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import ANY, Mock, patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
UI_DIRECTORY = SOURCE_DIRECTORY / "ui"
for caminho in (SOURCE_DIRECTORY, UI_DIRECTORY):
    if str(caminho) not in sys.path:
        sys.path.insert(0, str(caminho))

from controllers.relacao_controller import ResultadoCriarRelacionamento
from models import Objeto
from views.objeto_view import ObjetoView
from widgets.criar_relacionamento import CriarRelacionamento


def criar_objeto(objeto_id: int, titulo: str, tipo: str = "Nota") -> Objeto:
    return Objeto(
        id=objeto_id,
        titulo=titulo,
        tipo=tipo,
        caminho=None,
        resumo=None,
        hash_arquivo=None,
        status="ativo",
        data_criacao="2026-08-01",
        data_edicao="2026-08-01",
        data_exclusao=None,
    )


class CriarRelacionamentoTests(unittest.TestCase):
    def _widget_sem_tk(self) -> CriarRelacionamento:
        widget = object.__new__(CriarRelacionamento)
        widget._relacao_controller = Mock()
        widget._origem_id = 1
        widget._ao_criar_relacao = Mock()
        widget._termo_busca = ""
        widget._objeto_destino = None
        widget._criar_novo = False
        widget._entrada_busca = None
        widget._combo_tipo = None
        widget.estado = CriarRelacionamento.ESTADO_OCIOSO
        return widget

    def test_busca_muda_para_resultados_e_exclui_origem_via_controller(self) -> None:
        widget = self._widget_sem_tk()
        widget._entrada_busca = Mock(get=Mock(return_value="  estoicismo  "))
        resultado = criar_objeto(2, "Estoicismo", "PDF")
        widget._relacao_controller.buscar_objetos_para_relacionar.return_value = [resultado]
        widget._mostrar_resultados = Mock()

        widget._buscar()

        self.assertEqual(widget._termo_busca, "estoicismo")
        widget._relacao_controller.buscar_objetos_para_relacionar.assert_called_once_with(
            "estoicismo", 1
        )
        widget._mostrar_resultados.assert_called_once_with([resultado])

    def test_opcao_de_criar_novo_so_aparece_com_termo_nao_vazio(self) -> None:
        widget = self._widget_sem_tk()
        widget._limpar = Mock()
        widget.winfo_children = Mock(return_value=[])
        botoes: list[dict[str, object]] = []

        def criar_botao(*args: object, **kwargs: object) -> Mock:
            botoes.append(kwargs)
            return Mock(grid=Mock())

        with (
            patch("widgets.criar_relacionamento.ctk.CTkButton", side_effect=criar_botao),
            patch("widgets.criar_relacionamento.ctk.CTkLabel", return_value=Mock(grid=Mock())),
        ):
            widget._termo_busca = ""
            widget._mostrar_resultados([])
            textos_sem_termo = [botao["text"] for botao in botoes]

            botoes.clear()
            widget._termo_busca = "Nova nota"
            widget._mostrar_resultados([])
            textos_com_termo = [botao["text"] for botao in botoes]

        self.assertFalse(any("Criar novo objeto" in texto for texto in textos_sem_termo))
        self.assertIn("+ Criar novo objeto: 'Nova nota'", textos_com_termo)

    def test_selecao_de_resultado_avanca_para_tipo_de_relacao(self) -> None:
        widget = self._widget_sem_tk()
        objeto = criar_objeto(2, "Destino", "PDF")
        widget._mostrar_tipo_relacao = Mock()

        widget._selecionar_objeto(objeto)

        self.assertIs(widget._objeto_destino, objeto)
        self.assertFalse(widget._criar_novo)
        widget._mostrar_tipo_relacao.assert_called_once_with("Destino")

    def test_erro_de_relacao_duplicada_e_exibido(self) -> None:
        widget = self._widget_sem_tk()
        widget.mostrar_ocioso = Mock()

        with patch("widgets.criar_relacionamento.messagebox.showerror") as mostrar_erro:
            widget._ao_terminar_criacao(
                ResultadoCriarRelacionamento(
                    sucesso=False, mensagem_erro="relação já existe"
                )
            )

        mostrar_erro.assert_called_once_with(
            "Não foi possível criar o relacionamento", "relação já existe"
        )
        widget.mostrar_ocioso.assert_not_called()

    def test_sucesso_retorna_ao_ocioso_e_notifica_origem(self) -> None:
        widget = self._widget_sem_tk()
        widget.mostrar_ocioso = Mock()

        widget._ao_terminar_criacao(ResultadoCriarRelacionamento(sucesso=True))

        widget.mostrar_ocioso.assert_called_once_with()
        widget._ao_criar_relacao.assert_called_once_with(1)

    def test_confirmar_usa_tarefa_em_segundo_plano_para_objeto_existente(self) -> None:
        widget = self._widget_sem_tk()
        widget._objeto_destino = criar_objeto(2, "Destino")
        widget._combo_tipo = Mock(get=Mock(return_value="referência"))
        widget._ao_terminar_criacao = Mock()

        def executar_sincronamente(master, tarefa, ao_concluir, ao_falhar):
            ao_concluir(tarefa())

        with patch(
            "widgets.criar_relacionamento.executar_em_segundo_plano",
            side_effect=executar_sincronamente,
        ):
            widget._confirmar()

        widget._relacao_controller.criar.assert_called_once_with(1, 2, "referência")
        widget._ao_terminar_criacao.assert_called_once_with(
            widget._relacao_controller.criar.return_value
        )

    def test_confirmar_usa_tarefa_em_segundo_plano_para_novo_objeto(self) -> None:
        widget = self._widget_sem_tk()
        widget._criar_novo = True
        widget._termo_busca = "Nova nota"
        widget._combo_tipo = Mock(get=Mock(return_value="referência"))
        widget._ao_terminar_criacao = Mock()

        def executar_sincronamente(master, tarefa, ao_concluir, ao_falhar):
            ao_concluir(tarefa())

        with patch(
            "widgets.criar_relacionamento.executar_em_segundo_plano",
            side_effect=executar_sincronamente,
        ):
            widget._confirmar()

        widget._relacao_controller.criar_objeto_e_relacionar.assert_called_once_with(
            1, "Nova nota", "referência"
        )
        widget._ao_terminar_criacao.assert_called_once_with(
            widget._relacao_controller.criar_objeto_e_relacionar.return_value
        )

    def test_troca_de_objeto_nao_recarrega_tela_errada(self) -> None:
        view = object.__new__(ObjetoView)
        view._objeto_id_atual = 2
        view.mostrar_objeto = Mock()

        view._ao_criar_relacao(1)

        view.mostrar_objeto.assert_not_called()

    def test_objeto_view_entrega_controller_ao_widget(self) -> None:
        objeto = criar_objeto(1, "Origem")
        detalhe = SimpleNamespace(
            objeto=objeto, tags=[], relacionamentos=[], sugestoes=[]
        )
        view = object.__new__(ObjetoView)
        view._objeto_controller = Mock(carregar_detalhe=Mock(return_value=detalhe))
        view._tag_controller = Mock()
        view._relacao_controller = Mock()
        view._ao_editar_objeto = Mock()
        view._renderizar_tags_e_entrada = Mock()
        view._renderizar_secao_contexto = Mock(side_effect=lambda linha, **kwargs: linha + 1)
        view.winfo_children = Mock(return_value=[])

        with (
            patch("views.objeto_view.ctk.CTkFrame", return_value=Mock(grid_columnconfigure=Mock())),
            patch("views.objeto_view.ctk.CTkLabel", return_value=Mock(grid=Mock())),
            patch("views.objeto_view.ctk.CTkButton", return_value=Mock(grid=Mock())),
            patch("views.objeto_view.ctk.CTkFont"),
            patch(
                "views.objeto_view.CriarRelacionamento",
                return_value=Mock(grid=Mock()),
            ) as criar_widget,
        ):
            view.mostrar_objeto(1)

        criar_widget.assert_called_once_with(
            ANY,
            view._relacao_controller,
            1,
            ao_criar_relacao=view._ao_criar_relacao,
        )


if __name__ == "__main__":
    unittest.main()
