"""Servico de Backup e Restauracao do Acervo de Conhecimento (Fase 8).

Um backup completo, conforme docs/arquitetura.md (secao "Backup"),
precisa conter tres componentes juntos:

- banco.db     -- metadados (SQLite)
- acervo/      -- arquivos fisicos (PDFs, notas, documentos)
- vetores/     -- indice semantico (ChromaDB)

A ausencia de qualquer um torna o backup incompleto. Por isso o backup
e sempre um unico arquivo .zip autocontido, nunca uma copia solta dos
tres componentes -- assim o usuario nunca pode copiar só uma parte por
engano, nem apagar um dos tres sem apagar o backup inteiro junto.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import shutil
import sqlite3
import tempfile
import zipfile


NOME_BANCO = "banco.db"
NOME_ACERVO = "acervo"
NOME_VETORES = "vetores"

DEFAULT_CAMINHO_BANCO = Path(__file__).resolve().parents[2] / NOME_BANCO
DEFAULT_PASTA_ACERVO = Path(__file__).resolve().parents[2] / NOME_ACERVO
DEFAULT_PASTA_VETORES = Path(__file__).resolve().parents[2] / NOME_VETORES
DEFAULT_PASTA_BACKUPS = Path(__file__).resolve().parents[2] / "backups"


@dataclass
class ResultadoValidacao:
    """Resultado da checagem de integridade de um arquivo de backup."""

    valido: bool
    componentes_ausentes: list[str] = field(default_factory=list)
    mensagem_erro: str | None = None


@dataclass
class ResultadoBackup:
    """Resultado uniforme de uma tentativa de criar um backup."""

    sucesso: bool
    caminho: Path | None = None
    mensagem_erro: str | None = None


@dataclass
class ResultadoRestauracao:
    """Resultado uniforme de uma tentativa de restaurar um backup."""

    sucesso: bool
    mensagem_erro: str | None = None


class BackupService:
    """Cria, valida e restaura backups completos do Acervo."""

    def __init__(
        self,
        caminho_banco: Path | str = DEFAULT_CAMINHO_BANCO,
        pasta_acervo: Path | str = DEFAULT_PASTA_ACERVO,
        pasta_vetores: Path | str = DEFAULT_PASTA_VETORES,
        pasta_backups: Path | str = DEFAULT_PASTA_BACKUPS,
    ) -> None:
        self._caminho_banco = Path(caminho_banco)
        self._pasta_acervo = Path(pasta_acervo)
        self._pasta_vetores = Path(pasta_vetores)
        self._pasta_backups = Path(pasta_backups)

    def criar_backup(self) -> ResultadoBackup:
        """Cria um novo arquivo .zip com banco.db + acervo/ + vetores/.

        O nome do arquivo usa data e hora (wds_backup_AAAAMMDD_HHMMSS.zip)
        para nunca sobrescrever um backup anterior por engano.
        """
        try:
            if not self._caminho_banco.is_file():
                raise FileNotFoundError(
                    f"Banco de dados nao encontrado: {self._caminho_banco}"
                )

            self._pasta_backups.mkdir(parents=True, exist_ok=True)
            marca_tempo = datetime.now().strftime("%Y%m%d_%H%M%S")
            caminho_zip = self._pasta_backups / f"wds_backup_{marca_tempo}.zip"

            with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as zip_arquivo:
                self._gravar_banco_no_zip(zip_arquivo)
                self._gravar_pasta_no_zip(zip_arquivo, self._pasta_acervo, NOME_ACERVO)
                self._gravar_pasta_no_zip(zip_arquivo, self._pasta_vetores, NOME_VETORES)

            return ResultadoBackup(sucesso=True, caminho=caminho_zip)
        except Exception as erro:
            return ResultadoBackup(
                sucesso=False,
                mensagem_erro=f"Nao foi possivel criar o backup: {erro}",
            )

    def _gravar_banco_no_zip(self, zip_arquivo: zipfile.ZipFile) -> None:
        """Copia o banco de dados para dentro do zip usando a API de
        backup do proprio sqlite3, que produz uma copia consistente
        mesmo que outra conexao esteja escrevendo no banco no momento
        (ao contrario de uma copia de arquivo bruta, que poderia
        capturar um estado parcialmente escrito)."""
        with tempfile.TemporaryDirectory() as pasta_temporaria:
            copia_temporaria = Path(pasta_temporaria) / NOME_BANCO
            origem = sqlite3.connect(self._caminho_banco)
            try:
                destino = sqlite3.connect(copia_temporaria)
                try:
                    origem.backup(destino)
                finally:
                    destino.close()
            finally:
                origem.close()
            zip_arquivo.write(copia_temporaria, NOME_BANCO)

    def _gravar_pasta_no_zip(
        self,
        zip_arquivo: zipfile.ZipFile,
        pasta: Path,
        nome_no_zip: str,
    ) -> None:
        """Grava uma pasta inteira dentro do zip, preservando a estrutura
        relativa. Pastas ausentes ou vazias ainda contam como presentes
        no backup (grava uma entrada de diretorio vazia), para que a
        validacao de integridade nao rejeite um acervo legitimamente
        novo, sem nenhum arquivo ainda."""
        if not pasta.is_dir():
            zip_arquivo.writestr(f"{nome_no_zip}/", "")
            return

        arquivos = [item for item in pasta.rglob("*") if item.is_file()]
        if not arquivos:
            zip_arquivo.writestr(f"{nome_no_zip}/", "")
            return

        for item in arquivos:
            caminho_no_zip = f"{nome_no_zip}/{item.relative_to(pasta).as_posix()}"
            zip_arquivo.write(item, caminho_no_zip)

    def validar_integridade(self, caminho_backup: Path | str) -> ResultadoValidacao:
        """Verifica se um arquivo de backup contem os tres componentes
        obrigatorios (docs/arquitetura.md, secao "Backup"), sem
        restaurar nada -- apenas inspeciona o conteudo do zip."""
        caminho_backup = Path(caminho_backup)
        if not caminho_backup.is_file():
            return ResultadoValidacao(
                valido=False,
                mensagem_erro="Arquivo de backup nao encontrado.",
            )

        try:
            with zipfile.ZipFile(caminho_backup, "r") as zip_arquivo:
                nomes = zip_arquivo.namelist()
        except zipfile.BadZipFile:
            return ResultadoValidacao(
                valido=False,
                mensagem_erro="Arquivo de backup corrompido ou invalido.",
            )

        ausentes = []
        if NOME_BANCO not in nomes:
            ausentes.append(NOME_BANCO)
        if not any(nome.startswith(f"{NOME_ACERVO}/") for nome in nomes):
            ausentes.append(NOME_ACERVO)
        if not any(nome.startswith(f"{NOME_VETORES}/") for nome in nomes):
            ausentes.append(NOME_VETORES)

        if ausentes:
            return ResultadoValidacao(
                valido=False,
                componentes_ausentes=ausentes,
                mensagem_erro=(
                    "Backup incompleto: faltam os componentes "
                    f"{', '.join(ausentes)}."
                ),
            )

        return ResultadoValidacao(valido=True)

    def restaurar_backup(self, caminho_backup: Path | str) -> ResultadoRestauracao:
        """Restaura um backup valido, substituindo banco.db, acervo/ e
        vetores/ atuais pelos contidos no zip.

        Antes de sobrescrever qualquer coisa, guarda uma copia de
        seguranca do estado atual em uma pasta temporaria. Se qualquer
        etapa da extracao falhar no meio do processo, o estado anterior
        e restaurado a partir dessa copia -- o usuario nunca fica com
        um acervo pela metade por causa de uma restauracao malsucedida.

        Requer reiniciar a aplicacao apos a restauracao: os objetos em
        memoria (conexao do ChromaDB, cache de servicos) nao sao
        recarregados automaticamente.
        """
        validacao = self.validar_integridade(caminho_backup)
        if not validacao.valido:
            return ResultadoRestauracao(sucesso=False, mensagem_erro=validacao.mensagem_erro)

        caminho_backup = Path(caminho_backup)

        with tempfile.TemporaryDirectory() as pasta_temporaria:
            tmp = Path(pasta_temporaria)
            seguranca_banco = tmp / "seguranca_banco.db"
            seguranca_acervo = tmp / "seguranca_acervo"
            seguranca_vetores = tmp / "seguranca_vetores"

            try:
                if self._caminho_banco.is_file():
                    shutil.copy2(self._caminho_banco, seguranca_banco)
                if self._pasta_acervo.is_dir():
                    shutil.copytree(self._pasta_acervo, seguranca_acervo)
                if self._pasta_vetores.is_dir():
                    shutil.copytree(self._pasta_vetores, seguranca_vetores)
            except Exception as erro:
                return ResultadoRestauracao(
                    sucesso=False,
                    mensagem_erro=(
                        "Nao foi possivel preparar a copia de seguranca "
                        f"antes de restaurar; nada foi alterado: {erro}"
                    ),
                )

            try:
                with zipfile.ZipFile(caminho_backup, "r") as zip_arquivo:
                    if self._pasta_acervo.exists():
                        shutil.rmtree(self._pasta_acervo)
                    if self._pasta_vetores.exists():
                        shutil.rmtree(self._pasta_vetores)

                    pasta_extracao = tmp / "extraido"
                    zip_arquivo.extractall(pasta_extracao)

                    shutil.move(
                        str(pasta_extracao / NOME_BANCO), str(self._caminho_banco)
                    )
                    shutil.move(
                        str(pasta_extracao / NOME_ACERVO), str(self._pasta_acervo)
                    )
                    shutil.move(
                        str(pasta_extracao / NOME_VETORES), str(self._pasta_vetores)
                    )

                return ResultadoRestauracao(sucesso=True)

            except Exception as erro_restauracao:
                self._reverter_para_seguranca(
                    seguranca_banco, seguranca_acervo, seguranca_vetores
                )
                return ResultadoRestauracao(
                    sucesso=False,
                    mensagem_erro=(
                        "Falha ao restaurar; o estado anterior foi "
                        f"recuperado e nada foi perdido: {erro_restauracao}"
                    ),
                )

    def _reverter_para_seguranca(
        self,
        seguranca_banco: Path,
        seguranca_acervo: Path,
        seguranca_vetores: Path,
    ) -> None:
        """Restaura o estado anterior a partir da copia de seguranca,
        em melhor esforco -- usado quando uma restauracao falha no
        meio do processo."""
        if seguranca_banco.is_file():
            shutil.copy2(seguranca_banco, self._caminho_banco)
        if self._pasta_acervo.exists():
            shutil.rmtree(self._pasta_acervo)
        if seguranca_acervo.is_dir():
            shutil.copytree(seguranca_acervo, self._pasta_acervo)
        if self._pasta_vetores.exists():
            shutil.rmtree(self._pasta_vetores)
        if seguranca_vetores.is_dir():
            shutil.copytree(seguranca_vetores, self._pasta_vetores)

    def listar_backups(self) -> list[Path]:
        """Lista os backups existentes, do mais recente para o mais antigo."""
        if not self._pasta_backups.is_dir():
            return []
        return sorted(
            self._pasta_backups.glob("wds_backup_*.zip"),
            key=lambda caminho: caminho.name,
            reverse=True,
        )
