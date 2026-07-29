"""Servico de Configuracoes do sistema (Issue 27, EPIC 7).

O escopo de Configuracoes nao estava definido em nenhum documento do
projeto -- so havia uma linha em docs/interface-grafica.md
("Centraliza as configuracoes do sistema") e um config.json vazio
("{}") nunca lido por ninguem.

Decisao (nao especificada anteriormente, resolvida aqui): comecar com
apenas duas opcoes, escolhidas por serem as unicas coisas hoje
hardcoded no codigo que fazem sentido como preferencia pessoal, sem
mexer em nada estrutural (caminhos de armazenamento, por exemplo,
ficam de fora -- afetam Backup e todos os Services, mudanca grande
demais para decidir sem validar com o usuario primeiro):

- tema: aparencia da interface (CustomTkinter ja suporta nativamente).
- limite_resultados_semanticos: quantos resultados a busca por sentido
  traz por pesquisa (hoje fixo em 10 em PesquisaController).

Novas opcoes podem ser adicionadas aqui no futuro sem quebrar
config.json existentes -- carregar() sempre preenche com o default
qualquer chave ausente ou invalida, nunca falha por causa de um
arquivo desatualizado.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


TEMAS_VALIDOS = ("Sistema", "Claro", "Escuro")
LIMITE_MINIMO = 1
LIMITE_MAXIMO = 50
LIMITE_PADRAO = 10

DEFAULT_CAMINHO_CONFIG = Path(__file__).resolve().parents[2] / "config.json"

# Mapa entre o rotulo em portugues (salvo no config.json e mostrado na
# tela) e o valor que a API do CustomTkinter espera.
_TEMA_PARA_CTK = {"Sistema": "system", "Claro": "light", "Escuro": "dark"}


@dataclass
class Config:
    """Preferencias do usuario, com defaults seguros."""

    tema: str = "Sistema"
    limite_resultados_semanticos: int = LIMITE_PADRAO

    @property
    def tema_ctk(self) -> str:
        """Valor de tema no formato esperado por ctk.set_appearance_mode()."""
        return _TEMA_PARA_CTK[self.tema]


@dataclass
class ResultadoSalvarConfig:
    sucesso: bool
    mensagem_erro: str | None = None


class ConfigService:
    """Le e escreve as preferencias do usuario em config.json."""

    def __init__(self, caminho_config: Path | str = DEFAULT_CAMINHO_CONFIG) -> None:
        self._caminho_config = Path(caminho_config)

    def carregar(self) -> Config:
        """Le config.json e devolve um Config valido.

        Nunca lanca excecao por causa do arquivo: se ele nao existir,
        estiver corrompido, ou tiver uma chave/valor invalido, aquela
        chave especifica cai para o default -- um config.json antigo
        ou parcialmente escrito nunca impede o WDS de abrir.
        """
        dados: dict = {}
        if self._caminho_config.is_file():
            try:
                dados = json.loads(self._caminho_config.read_text(encoding="utf-8"))
                if not isinstance(dados, dict):
                    dados = {}
            except (json.JSONDecodeError, OSError):
                dados = {}

        tema = dados.get("tema")
        if tema not in TEMAS_VALIDOS:
            tema = "Sistema"

        limite = dados.get("limite_resultados_semanticos")
        if not isinstance(limite, int) or not (LIMITE_MINIMO <= limite <= LIMITE_MAXIMO):
            limite = LIMITE_PADRAO

        return Config(tema=tema, limite_resultados_semanticos=limite)

    def salvar(self, config: Config) -> ResultadoSalvarConfig:
        """Valida e persiste as preferencias em config.json.

        Escrita atomica (arquivo temporario + os.replace), mesmo
        padrao ja usado por EditorMarkdownController, para nunca
        deixar um config.json pela metade se o processo for
        interrompido no meio da escrita.
        """
        if config.tema not in TEMAS_VALIDOS:
            return ResultadoSalvarConfig(
                sucesso=False,
                mensagem_erro=(
                    f"Tema invalido: '{config.tema}'. "
                    f"Use um destes: {', '.join(TEMAS_VALIDOS)}."
                ),
            )
        if not (LIMITE_MINIMO <= config.limite_resultados_semanticos <= LIMITE_MAXIMO):
            return ResultadoSalvarConfig(
                sucesso=False,
                mensagem_erro=(
                    "Quantidade de resultados semanticos deve estar entre "
                    f"{LIMITE_MINIMO} e {LIMITE_MAXIMO}."
                ),
            )

        try:
            import os
            import tempfile

            dados = {
                "tema": config.tema,
                "limite_resultados_semanticos": config.limite_resultados_semanticos,
            }
            self._caminho_config.parent.mkdir(parents=True, exist_ok=True)
            descritor, caminho_temporario = tempfile.mkstemp(
                dir=self._caminho_config.parent, suffix=".tmp"
            )
            try:
                with os.fdopen(descritor, "w", encoding="utf-8") as arquivo:
                    json.dump(dados, arquivo, ensure_ascii=False, indent=2)
                os.replace(caminho_temporario, self._caminho_config)
            except Exception:
                Path(caminho_temporario).unlink(missing_ok=True)
                raise

            return ResultadoSalvarConfig(sucesso=True)
        except OSError as erro:
            return ResultadoSalvarConfig(
                sucesso=False,
                mensagem_erro=f"Nao foi possivel salvar as configuracoes: {erro}",
            )
