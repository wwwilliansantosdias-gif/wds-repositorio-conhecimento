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
        self, tags: list[Tag]
    ) -> tuple[list[dict[str, object]], list[dict[str, object]], Mock]:
        panel = object.__new__(TagsPanel)
        panel._tag_controller = Mock(listar_todas=Mock(return_value=tags))
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
        self.assertEqual(len(labels_criados), 1)
        self.assertEqual(labels_criados[0]["text"], "Nenhuma tag cadastrada ainda.")

    def test_painel_nao_oferece_nenhuma_acao_de_exclusao(self) -> None:
        tags = [Tag(id=1, nome="python")]

        _, chips_criados, _ = self._atualizar_e_capturar(tags)

        self.assertIsNone(chips_criados[0]["ao_remover"])


if __name__ == "__main__":
    unittest.main()
