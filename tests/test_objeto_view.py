"""Testes do painel de Objeto em Foco."""

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

from controllers.tag_controller import ResultadoAdicionarTag
from models import Objeto, Tag
from views.objeto_view import LIMITE_RESUMO_DETALHE, LIMITE_TITULO_TRILHA, ObjetoView
from widgets.resultado_item import (
    COR_SCORE_FORTE,
    COR_SCORE_FRACO,
    COR_SCORE_MEDIO,
    estilo_por_score,
)


class ObjetoViewTests(unittest.TestCase):
    def _criar_objeto(
        self, tipo: str, caminho: str, resumo: str | None = None
    ) -> Objeto:
        return Objeto(
            id=1,
            titulo="Objeto de teste",
            tipo=tipo,
            caminho=caminho,
            resumo=resumo,
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

    def _mostrar_objeto_e_capturar_labels(self, resumo: str) -> list[dict[str, object]]:
        objeto = self._criar_objeto("PDF", r"C:\\acervo\\pdfs\\1.pdf", resumo)
        detalhe = SimpleNamespace(
            objeto=objeto,
            tags=[],
            relacionamentos=[],
            sugestoes=[],
        )
        view = object.__new__(ObjetoView)
        view._objeto_controller = Mock(carregar_detalhe=Mock(return_value=detalhe))
        view._ao_editar_objeto = Mock()
        view._renderizar_tags_e_entrada = Mock()
        view._renderizar_secao_contexto = Mock(side_effect=lambda linha, **kwargs: linha + 1)
        view.winfo_children = Mock(return_value=[])

        labels_criados: list[dict[str, object]] = []

        def criar_label(*args: object, **kwargs: object) -> Mock:
            labels_criados.append(kwargs)
            return Mock()

        with (
            patch("views.objeto_view.ctk.CTkFrame", return_value=Mock()),
            patch("views.objeto_view.ctk.CTkLabel", side_effect=criar_label),
            patch("views.objeto_view.ctk.CTkButton", return_value=Mock()),
            patch("views.objeto_view.ctk.CTkFont"),
        ):
            view.mostrar_objeto(1)

        return labels_criados

    def test_resumo_longo_e_truncado_no_painel_de_detalhe(self) -> None:
        resumo_longo = "x" * 5000
        labels = self._mostrar_objeto_e_capturar_labels(resumo_longo)

        textos_resumo = [
            kwargs["text"]
            for kwargs in labels
            if isinstance(kwargs.get("text"), str) and kwargs["text"].startswith("x")
        ]

        self.assertEqual(len(textos_resumo), 1)
        texto_resumo = textos_resumo[0]
        self.assertLessEqual(
            len(texto_resumo), LIMITE_RESUMO_DETALHE + len("... (truncado)")
        )
        self.assertTrue(texto_resumo.endswith("... (truncado)"))

    def test_resumo_curto_nao_e_truncado(self) -> None:
        resumo_curto = "Um resumo qualquer, bem curto."
        labels = self._mostrar_objeto_e_capturar_labels(resumo_curto)

        textos_resumo = [kwargs["text"] for kwargs in labels if kwargs.get("text") == resumo_curto]

        self.assertEqual(len(textos_resumo), 1)

    def _mostrar_objeto_e_capturar_miniaturas(
        self, tipo: str
    ) -> list[dict[str, object]]:
        objeto = self._criar_objeto(tipo, r"C:\\acervo\\imagens\\1.png", "Descricao.")
        detalhe = SimpleNamespace(
            objeto=objeto,
            tags=[],
            relacionamentos=[],
            sugestoes=[],
        )
        view = object.__new__(ObjetoView)
        view._objeto_controller = Mock(carregar_detalhe=Mock(return_value=detalhe))
        view._ao_editar_objeto = Mock()
        view._renderizar_tags_e_entrada = Mock()
        view._renderizar_secao_contexto = Mock(side_effect=lambda linha, **kwargs: linha + 1)
        view.winfo_children = Mock(return_value=[])

        miniaturas_criadas: list[dict[str, object]] = []

        def criar_miniatura(master: object, caminho: object, **kwargs: object) -> Mock:
            miniaturas_criadas.append({"caminho": caminho})
            widget = Mock()
            widget.grid = Mock()
            return widget

        with (
            patch("views.objeto_view.ctk.CTkFrame", return_value=Mock()),
            patch("views.objeto_view.ctk.CTkLabel", return_value=Mock()),
            patch("views.objeto_view.ctk.CTkButton", return_value=Mock()),
            patch("views.objeto_view.ctk.CTkFont"),
            patch("views.objeto_view.MiniaturaImagem", side_effect=criar_miniatura),
        ):
            view.mostrar_objeto(1)

        return miniaturas_criadas

    def test_miniatura_e_exibida_apenas_para_objetos_do_tipo_imagem(self) -> None:
        for tipo, deve_exibir in (("Imagem", True), ("PDF", False), ("Nota", False)):
            with self.subTest(tipo=tipo):
                miniaturas = self._mostrar_objeto_e_capturar_miniaturas(tipo)
                self.assertEqual(len(miniaturas) == 1, deve_exibir)
                if miniaturas:
                    self.assertEqual(
                        miniaturas[0]["caminho"], r"C:\\acervo\\imagens\\1.png"
                    )

    def test_rotulo_do_texto_pesquisavel_e_descricao_para_imagem(self) -> None:
        objeto = self._criar_objeto(
            "Imagem", r"C:\\acervo\\imagens\\1.png", "Uma bela paisagem."
        )
        detalhe = SimpleNamespace(
            objeto=objeto, tags=[], relacionamentos=[], sugestoes=[]
        )
        view = object.__new__(ObjetoView)
        view._objeto_controller = Mock(carregar_detalhe=Mock(return_value=detalhe))
        view._ao_editar_objeto = Mock()
        view._renderizar_tags_e_entrada = Mock()
        view._renderizar_secao_contexto = Mock(side_effect=lambda linha, **kwargs: linha + 1)
        view.winfo_children = Mock(return_value=[])

        labels_criados: list[dict[str, object]] = []

        def criar_label(*args: object, **kwargs: object) -> Mock:
            labels_criados.append(kwargs)
            return Mock()

        with (
            patch("views.objeto_view.ctk.CTkFrame", return_value=Mock()),
            patch("views.objeto_view.ctk.CTkLabel", side_effect=criar_label),
            patch("views.objeto_view.ctk.CTkButton", return_value=Mock()),
            patch("views.objeto_view.ctk.CTkFont"),
            patch("views.objeto_view.MiniaturaImagem", return_value=Mock(grid=Mock())),
        ):
            view.mostrar_objeto(1)

        textos = [kwargs.get("text") for kwargs in labels_criados]
        self.assertIn("Descrição", textos)
        self.assertNotIn("Resumo", textos)

    def _renderizar_contexto_teste(
        self,
        quantidade: int,
        limite_padrao: int | None,
        expandido: bool = False,
    ) -> tuple[list[Mock], list[dict[str, object]]]:
        view = object.__new__(ObjetoView)
        view._tag_controller = Mock(listar_por_objeto=Mock(return_value=[]))
        view._ao_selecionar_objeto = Mock()
        view._sugestoes_expandido = expandido
        objetos = [self._criar_objeto("Nota", "", f"Resumo {indice}") for indice in range(quantidade)]
        itens: list[Mock] = []
        botoes: list[dict[str, object]] = []

        def criar_item(*args: object, **kwargs: object) -> Mock:
            item = Mock()
            item.grid = Mock()
            itens.append(item)
            return item

        def criar_botao(*args: object, **kwargs: object) -> Mock:
            botoes.append(kwargs)
            return Mock(grid=Mock())

        with (
            patch("views.objeto_view.ctk.CTkLabel", return_value=Mock(grid=Mock())),
            patch("views.objeto_view.ctk.CTkButton", side_effect=criar_botao),
            patch("views.objeto_view.ctk.CTkFont"),
            patch("views.objeto_view.ResultadoItem", side_effect=criar_item),
        ):
            view._renderizar_secao_contexto(
                0,
                "Sugestoes",
                [(objeto, 80.0) for objeto in objetos],
                "Nenhuma",
                limite_padrao=limite_padrao,
            )

        return itens, botoes

    def test_sugestoes_com_mais_de_tres_mostra_tres_e_ver_mais(self) -> None:
        itens, botoes = self._renderizar_contexto_teste(5, 3)

        self.assertEqual(len(itens), 3)
        self.assertEqual([botao["text"] for botao in botoes], ["Ver mais (2)"])

    def test_sugestoes_com_tres_ou_menos_nao_mostra_ver_mais(self) -> None:
        for quantidade in (0, 1, 3):
            with self.subTest(quantidade=quantidade):
                itens, botoes = self._renderizar_contexto_teste(quantidade, 3)
                self.assertEqual(len(itens), quantidade)
                self.assertFalse(botoes)

    def test_ver_mais_expande_sugestoes_para_lista_completa(self) -> None:
        view = object.__new__(ObjetoView)
        view._objeto_id_atual = 42
        view._sugestoes_expandido = False
        view.mostrar_objeto = Mock()

        view._expandir_sugestoes()

        self.assertTrue(view._sugestoes_expandido)
        view.mostrar_objeto.assert_called_once_with(42)

    def test_relacionamentos_nao_sao_limitados(self) -> None:
        itens, botoes = self._renderizar_contexto_teste(5, None)

        self.assertEqual(len(itens), 5)
        self.assertFalse(botoes)

    @staticmethod
    def _executar_sincronamente_e_trocar_objeto(view: ObjetoView, novo_objeto_id: int):
        """Fake de executar_em_segundo_plano: roda a tarefa e chama
        ao_concluir imediatamente (sem thread de verdade), mas simula o
        usuario trocando de objeto ANTES da tarefa terminar -- exatamente
        a condicao de corrida que _ao_terminar_adicionar_tag/
        _ao_terminar_remover_tag precisam tratar."""

        def fake_executar(master, tarefa, ao_concluir, ao_falhar=None):
            resultado = tarefa()
            view._objeto_id_atual = novo_objeto_id
            ao_concluir(resultado)

        return fake_executar

    @staticmethod
    def _executar_sincronamente(master, tarefa, ao_concluir, ao_falhar=None):
        """Fake de executar_em_segundo_plano sem troca de objeto no meio --
        caminho feliz, objeto atual continua o mesmo ate a tarefa terminar."""
        ao_concluir(tarefa())

    def test_adicionar_tag_atualiza_a_tela_quando_objeto_atual_nao_mudou(self) -> None:
        view = object.__new__(ObjetoView)
        view._objeto_id_atual = 1
        view._tag_controller = Mock(
            adicionar_tag=Mock(
                return_value=ResultadoAdicionarTag(
                    sucesso=True, tag=Tag(id=1, nome="python")
                )
            )
        )
        view.mostrar_objeto = Mock()
        entrada = Mock(get=Mock(return_value="python"))

        with patch(
            "views.objeto_view.executar_em_segundo_plano",
            side_effect=self._executar_sincronamente,
        ):
            view._adicionar_tag(entrada)

        view._tag_controller.adicionar_tag.assert_called_once_with(1, "python")
        view.mostrar_objeto.assert_called_once_with(1)

    def test_adicionar_tag_nao_atualiza_a_tela_se_o_objeto_atual_mudou_no_meio(
        self,
    ) -> None:
        view = object.__new__(ObjetoView)
        view._objeto_id_atual = 1
        view._tag_controller = Mock(
            adicionar_tag=Mock(
                return_value=ResultadoAdicionarTag(
                    sucesso=True, tag=Tag(id=1, nome="python")
                )
            )
        )
        view.mostrar_objeto = Mock()
        entrada = Mock(get=Mock(return_value="python"))

        with patch(
            "views.objeto_view.executar_em_segundo_plano",
            side_effect=self._executar_sincronamente_e_trocar_objeto(view, 2),
        ):
            view._adicionar_tag(entrada)

        view.mostrar_objeto.assert_not_called()

    def test_remover_tag_atualiza_a_tela_quando_objeto_atual_nao_mudou(self) -> None:
        view = object.__new__(ObjetoView)
        view._objeto_id_atual = 1
        view._tag_controller = Mock(remover_tag=Mock(return_value=None))
        view.mostrar_objeto = Mock()

        with patch(
            "views.objeto_view.executar_em_segundo_plano",
            side_effect=self._executar_sincronamente,
        ):
            view._remover_tag(42)

        view._tag_controller.remover_tag.assert_called_once_with(1, 42)
        view.mostrar_objeto.assert_called_once_with(1)

    def test_remover_tag_nao_atualiza_a_tela_se_o_objeto_atual_mudou_no_meio(
        self,
    ) -> None:
        view = object.__new__(ObjetoView)
        view._objeto_id_atual = 1
        view._tag_controller = Mock(remover_tag=Mock(return_value=None))
        view.mostrar_objeto = Mock()

        with patch(
            "views.objeto_view.executar_em_segundo_plano",
            side_effect=self._executar_sincronamente_e_trocar_objeto(view, 2),
        ):
            view._remover_tag(42)

        view.mostrar_objeto.assert_not_called()

    def test_falha_inesperada_ao_alterar_tag_mostra_mensagem_de_erro(self) -> None:
        view = object.__new__(ObjetoView)
        view._objeto_id_atual = 1
        view._tag_controller = Mock(
            adicionar_tag=Mock(side_effect=RuntimeError("falha simulada"))
        )
        view.mostrar_objeto = Mock()
        entrada = Mock(get=Mock(return_value="python"))

        def fake_executar(master, tarefa, ao_concluir, ao_falhar=None):
            try:
                resultado = tarefa()
            except Exception as erro:  # noqa: BLE001 - mesmo padrao do modulo real
                ao_falhar(erro)
            else:
                ao_concluir(resultado)

        with (
            patch("views.objeto_view.executar_em_segundo_plano", side_effect=fake_executar),
            patch("views.objeto_view.messagebox.showerror") as mostrar_erro,
        ):
            view._adicionar_tag(entrada)

        mostrar_erro.assert_called_once()
        view.mostrar_objeto.assert_not_called()


class TrilhaAssociativaTests(unittest.TestCase):
    """Item A.1: trilha de navegacao dentro de Objeto em Foco."""

    @staticmethod
    def _criar_view(objeto_id: int | None, titulo: str = "Atual") -> ObjetoView:
        view = object.__new__(ObjetoView)
        view._objeto_id_atual = objeto_id
        view._titulo_atual = titulo
        view._trilha = []
        view._manter_trilha = False
        view._sugestoes_expandido = False
        return view

    @staticmethod
    def _mostrar(view: ObjetoView, objeto_id: int, titulo: str = "Novo") -> None:
        objeto = Objeto(
            id=objeto_id,
            titulo=titulo,
            tipo="Nota",
            caminho="x",
            resumo=None,
            hash_arquivo=None,
            status="ativo",
            data_criacao="2026-08-01T10:00:00+00:00",
            data_edicao="2026-08-01T10:00:00+00:00",
            data_exclusao=None,
        )
        detalhe = SimpleNamespace(
            objeto=objeto, tags=[], relacionamentos=[], sugestoes=[]
        )
        view._objeto_controller = Mock(carregar_detalhe=Mock(return_value=detalhe))
        view._ao_editar_objeto = Mock()
        view._relacao_controller = None
        view._renderizar_tags_e_entrada = Mock()
        view._renderizar_secao_contexto = Mock(side_effect=lambda linha, **kwargs: linha + 1)
        view._renderizar_trilha = Mock()
        view.winfo_children = Mock(return_value=[])
        with (
            patch("views.objeto_view.ctk.CTkFrame", return_value=Mock()),
            patch("views.objeto_view.ctk.CTkLabel", return_value=Mock()),
            patch("views.objeto_view.ctk.CTkButton", return_value=Mock()),
            patch("views.objeto_view.ctk.CTkFont"),
        ):
            view.mostrar_objeto(objeto_id)

    def test_clique_no_contexto_registra_objeto_atual_e_navega_com_flag(self) -> None:
        view = self._criar_view(1, "Primeiro")
        flags: list[bool] = []
        view._ao_selecionar_objeto = Mock(
            side_effect=lambda _id: flags.append(view._manter_trilha)
        )

        view._ao_selecionar_pelo_contexto(2)

        self.assertEqual(view._trilha, [(1, "Primeiro")])
        view._ao_selecionar_objeto.assert_called_once_with(2)
        self.assertEqual(flags, [True])
        self.assertFalse(view._manter_trilha)

    def test_flag_e_limpo_mesmo_se_o_callback_externo_falhar(self) -> None:
        view = self._criar_view(1)
        view._ao_selecionar_objeto = Mock(side_effect=RuntimeError("falha"))

        with self.assertRaises(RuntimeError):
            view._ao_selecionar_pelo_contexto(2)

        self.assertFalse(view._manter_trilha)

    def test_trilha_cresce_a_cada_clique_no_contexto(self) -> None:
        view = self._criar_view(1, "A")
        view._ao_selecionar_objeto = Mock(
            side_effect=lambda objeto_id: self._mostrar(view, objeto_id, f"T{objeto_id}")
        )

        view._ao_selecionar_pelo_contexto(2)
        view._ao_selecionar_pelo_contexto(3)

        self.assertEqual(view._trilha, [(1, "A"), (2, "T2")])
        self.assertEqual(view._objeto_id_atual, 3)

    def test_outra_forma_de_chegar_a_um_objeto_reinicia_a_trilha(self) -> None:
        view = self._criar_view(2, "B")
        view._trilha = [(1, "A")]

        self._mostrar(view, 9)

        self.assertEqual(view._trilha, [])

    def test_recarregar_o_mesmo_objeto_preserva_a_trilha(self) -> None:
        view = self._criar_view(2, "B")
        view._trilha = [(1, "A")]

        self._mostrar(view, 2)

        self.assertEqual(view._trilha, [(1, "A")])

    def test_espaco_reservado_limpa_a_trilha(self) -> None:
        view = self._criar_view(2)
        view._trilha = [(1, "A")]
        view.winfo_children = Mock(return_value=[])
        view.grid_columnconfigure = Mock()

        with patch("views.objeto_view.ctk.CTkLabel", return_value=Mock()):
            view.mostrar_espaco_reservado()

        self.assertEqual(view._trilha, [])

    def test_voltar_na_trilha_descarta_o_que_vinha_depois(self) -> None:
        view = self._criar_view(4, "D")
        view._trilha = [(1, "A"), (2, "B"), (3, "C")]
        view._ao_selecionar_objeto = Mock(
            side_effect=lambda objeto_id: self._mostrar(view, objeto_id)
        )

        view._voltar_na_trilha(1)

        view._ao_selecionar_objeto.assert_called_once_with(2)
        self.assertEqual(view._trilha, [(1, "A")])

    def test_trilha_so_e_renderizada_quando_nao_esta_vazia(self) -> None:
        view = self._criar_view(None)
        self._mostrar(view, 1)
        view._renderizar_trilha.assert_not_called()

        view._trilha = [(1, "A")]
        view._manter_trilha = True
        self._mostrar(view, 2)
        view._renderizar_trilha.assert_called_once_with(0)

    def test_titulo_longo_e_abreviado_na_trilha(self) -> None:
        longo = "x" * 60

        abreviado = ObjetoView._abreviar_titulo(longo)

        self.assertEqual(len(abreviado), LIMITE_TITULO_TRILHA)
        self.assertTrue(abreviado.endswith("…"))
        self.assertEqual(ObjetoView._abreviar_titulo("curto"), "curto")


class PesoVisualPorScoreTests(unittest.TestCase):
    """Item A.2: cor do score das Sugestoes Semanticas."""

    def test_score_forte_usa_cor_de_destaque(self) -> None:
        for score in (75.0, 90.0, 100.0):
            with self.subTest(score=score):
                self.assertEqual(estilo_por_score(score), (COR_SCORE_FORTE, None))

    def test_score_medio_mantem_o_visual_atual(self) -> None:
        for score in (50.0, 62.0, 74.9):
            with self.subTest(score=score):
                self.assertEqual(estilo_por_score(score), (COR_SCORE_MEDIO, None))

    def test_score_fraco_apaga_score_e_titulo(self) -> None:
        for score in (0.0, 30.0, 49.9):
            with self.subTest(score=score):
                self.assertEqual(
                    estilo_por_score(score), (COR_SCORE_FRACO, COR_SCORE_FRACO)
                )

    def test_secao_de_contexto_so_pesa_sugestoes_com_score(self) -> None:
        view = object.__new__(ObjetoView)
        view._sugestoes_expandido = False
        view._tag_controller = Mock(listar_por_objeto=Mock(return_value=[]))
        view._ao_selecionar_objeto = Mock()
        objeto = Mock(id=1)

        with (
            patch("views.objeto_view.ctk.CTkLabel", return_value=Mock()),
            patch("views.objeto_view.ctk.CTkFont"),
            patch("views.objeto_view.ResultadoItem") as item,
        ):
            view._renderizar_secao_contexto(0, "Rel", [(objeto, None)], "vazio")
            view._renderizar_secao_contexto(0, "Sug", [(objeto, 80.0)], "vazio")

        pesos = [chamada.kwargs["peso_visual_por_score"] for chamada in item.call_args_list]
        self.assertEqual(pesos, [False, True])


if __name__ == "__main__":
    unittest.main()
