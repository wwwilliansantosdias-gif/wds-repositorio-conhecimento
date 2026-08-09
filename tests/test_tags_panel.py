"""Testes do painel fixo de tags."""

from __future__ import annotations

from pathlib import Path
import sys
from unittest.mock import Mock, patch
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
UI_DIRECTORY = SOURCE_DIRECTORY / "ui"
for caminho in (SOURCE_DIRECTORY, UI_DIRECTORY):
    if str(caminho) not in sys.path:
        sys.path.insert(0, str(caminho))

from models import Tag
from widgets.tags_panel import TagsPanel


class TagsPanelTests(unittest.TestCase):
    def _atualizar_e_capturar(
        self, tags: list[Tag], total_ativos: int = 0
    ) -> tuple[list[dict[str, object]], list[dict[str, object]], Mock]:
        panel = object.__new__(TagsPanel)
        panel._tag_controller = Mock(listar_todas=Mock(return_value=tags))
        panel._acervo_service = Mock(contar_ativos=Mock(return_value=total_ativos))
        panel._ao_selecionar_tag = Mock()
        panel.winfo_children = Mock(return_value=[])

        labels_criados: list[dict[str, object]] = []
        chips_criados: list[dict[str, object]] = []

        def criar_label(*args: object, **kwargs: object) -> Mock:
            labels_criados.append(kwargs)
            return Mock()

        def criar_chip(
            master: object, tag: Tag, ao_remover: object = None, **kwargs: object
        ) -> Mock:
            chips_criados.append({"tag": tag, "ao_remover": ao_remover, **kwargs})
            return Mock()

        with (
            patch("widgets.tags_panel.ctk.CTkLabel", side_effect=criar_label),
            patch("widgets.tags_panel.ctk.CTkFont"),
            patch("widgets.tags_panel.TagChip", side_effect=criar_chip),
        ):
            panel.atualizar()

        return labels_criados, chips_criados, panel._ao_selecionar_tag

    def test_lista_as_tags_corretas(self) -> None:
        tags = [Tag(id=1, nome="python"), Tag(id=2, nome="livros")]

        _, chips_criados, _ = self._atualizar_e_capturar(tags)

        self.assertEqual([chip["tag"] for chip in chips_criados], tags)

    def test_clique_em_tag_dispara_callback_de_busca_com_o_nome_certo(self) -> None:
        tags = [Tag(id=1, nome="python")]

        _, chips_criados, callback = self._atualizar_e_capturar(tags)

        self.assertIs(chips_criados[0]["ao_selecionar"], callback)
        chips_criados[0]["ao_selecionar"]("python")
        callback.assert_called_once_with("python")

    def test_estado_vazio_quando_nao_ha_tags(self) -> None:
        labels_criados, chips_criados, _ = self._atualizar_e_capturar([])

        self.assertEqual(chips_criados, [])
        # Um label e sempre criado (o contador); com lista vazia de tags,
        # o segundo label e a mensagem de estado vazio.
        self.assertEqual(len(labels_criados), 2)
        self.assertEqual(labels_criados[1]["text"], "Nenhuma tag cadastrada ainda.")

    def test_painel_nao_oferece_nenhuma_acao_de_exclusao(self) -> None:
        tags = [Tag(id=1, nome="python")]

        _, chips_criados, _ = self._atualizar_e_capturar(tags)

        self.assertIsNone(chips_criados[0]["ao_remover"])

    def test_contador_exibe_o_total_de_objetos_ativos(self) -> None:
        labels_criados, _, _ = self._atualizar_e_capturar([], total_ativos=42)

        self.assertEqual(labels_criados[0]["text"], "42 objetos no acervo")

    def test_contador_usa_singular_para_um_objeto(self) -> None:
        labels_criados, _, _ = self._atualizar_e_capturar([], total_ativos=1)

        self.assertEqual(labels_criados[0]["text"], "1 objeto no acervo")

    def test_contador_usa_plural_para_zero_objetos(self) -> None:
        labels_criados, _, _ = self._atualizar_e_capturar([], total_ativos=0)

        self.assertEqual(labels_criados[0]["text"], "0 objetos no acervo")

    def test_atualizar_recarrega_o_contador_ao_ser_chamado_de_novo(self) -> None:
        panel = object.__new__(TagsPanel)
        panel._tag_controller = Mock(listar_todas=Mock(return_value=[]))
        panel._acervo_service = Mock(contar_ativos=Mock(return_value=5))
        panel._ao_selecionar_tag = Mock()
        panel.winfo_children = Mock(return_value=[])

        labels_criados: list[dict[str, object]] = []

        def criar_label(*args: object, **kwargs: object) -> Mock:
            labels_criados.append(kwargs)
            return Mock()

        with (
            patch("widgets.tags_panel.ctk.CTkLabel", side_effect=criar_label),
            patch("widgets.tags_panel.ctk.CTkFont"),
        ):
            panel.atualizar()
            panel._acervo_service.contar_ativos.return_value = 6
            panel.atualizar()

        self.assertEqual(labels_criados[0]["text"], "5 objetos no acervo")
        self.assertEqual(labels_criados[2]["text"], "6 objetos no acervo")


if __name__ == "__main__":
    unittest.main()
