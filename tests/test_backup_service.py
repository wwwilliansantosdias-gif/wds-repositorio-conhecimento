"""Testes do BackupService -- criar, validar e restaurar backups."""

from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
import zipfile
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from persistence import Database
from services.acervo_service import AcervoService
from services.backup_service import BackupService
from services.importacao_service import ImportacaoService
from services.objeto_service import ObjetoService


class EmbeddingServiceStub:
    """Substituto do EmbeddingService que evita carregar o modelo real
    (e depender de rede) nestes testes, focados no ciclo de arquivos
    de backup, nao em busca semantica."""

    def indexar_objeto(self, *args, **kwargs) -> None:
        pass

    def remover_do_indice(self, *args, **kwargs) -> None:
        pass


class BackupServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        temporary_path = Path(self.temporary_directory.name)
        self.addCleanup(self.temporary_directory.cleanup)

        self.caminho_banco = temporary_path / "banco.db"
        self.pasta_acervo = temporary_path / "acervo"
        self.pasta_vetores = temporary_path / "vetores"
        self.pasta_backups = temporary_path / "backups"

        self.database = Database(self.caminho_banco)
        self.database.initialize()

        objeto_service = ObjetoService(self.database)
        acervo_service = AcervoService(objeto_service, EmbeddingServiceStub())
        self.importacao_service = ImportacaoService(
            acervo_service,
            pasta_pdfs=self.pasta_acervo / "pdfs",
            pasta_notas=self.pasta_acervo / "notas",
            pasta_documentos=self.pasta_acervo / "documentos",
        )

        # Simula um indice ChromaDB real (o BackupService so precisa
        # saber copiar a pasta -- nao interpreta o conteudo).
        self.pasta_vetores.mkdir(parents=True, exist_ok=True)
        (self.pasta_vetores / "chroma.sqlite3").write_text("indice falso")

        self.backup_service = BackupService(
            caminho_banco=self.caminho_banco,
            pasta_acervo=self.pasta_acervo,
            pasta_vetores=self.pasta_vetores,
            pasta_backups=self.pasta_backups,
        )

    def _criar_nota(self, titulo: str, conteudo: str):
        return self.importacao_service.criar_nota_manual(titulo, conteudo=conteudo)

    # -- Criacao ----------------------------------------------------

    def test_criar_backup_gera_zip_com_os_tres_componentes(self) -> None:
        self._criar_nota("Nota de teste", "conteudo da nota")

        resultado = self.backup_service.criar_backup()

        self.assertTrue(resultado.sucesso, resultado.mensagem_erro)
        self.assertTrue(resultado.caminho.is_file())

        with zipfile.ZipFile(resultado.caminho) as zip_arquivo:
            nomes = zip_arquivo.namelist()
            self.assertIn("banco.db", nomes)
            self.assertTrue(any(nome.startswith("acervo/") for nome in nomes))
            self.assertTrue(any(nome.startswith("vetores/") for nome in nomes))
            self.assertIn("vetores/chroma.sqlite3", nomes)

    def test_criar_backup_falha_se_banco_nao_existir(self) -> None:
        self.caminho_banco.unlink()

        resultado = self.backup_service.criar_backup()

        self.assertFalse(resultado.sucesso)
        self.assertIn("Banco de dados nao encontrado", resultado.mensagem_erro)

    def test_criar_backup_funciona_com_acervo_vazio(self) -> None:
        """Um acervo recem-criado, sem nenhum arquivo ainda, deve gerar
        um backup valido (pastas vazias contam como presentes)."""
        resultado = self.backup_service.criar_backup()

        self.assertTrue(resultado.sucesso, resultado.mensagem_erro)
        validacao = self.backup_service.validar_integridade(resultado.caminho)
        self.assertTrue(validacao.valido, validacao.mensagem_erro)

    def test_listar_backups_ordena_do_mais_recente_para_o_mais_antigo(self) -> None:
        primeiro = self.backup_service.criar_backup()
        segundo_nome = self.pasta_backups / "wds_backup_99991231_235959.zip"
        self.pasta_backups.mkdir(parents=True, exist_ok=True)
        segundo_nome.write_bytes(primeiro.caminho.read_bytes())

        backups = self.backup_service.listar_backups()

        self.assertEqual(backups[0], segundo_nome)
        self.assertEqual(backups[1], primeiro.caminho)

    # -- Validacao ----------------------------------------------------

    def test_validar_integridade_aceita_backup_completo(self) -> None:
        self._criar_nota("Nota", "conteudo")
        resultado = self.backup_service.criar_backup()

        validacao = self.backup_service.validar_integridade(resultado.caminho)

        self.assertTrue(validacao.valido)
        self.assertEqual(validacao.componentes_ausentes, [])

    def test_validar_integridade_rejeita_zip_sem_vetores(self) -> None:
        caminho_incompleto = self.pasta_backups / "wds_backup_incompleto.zip"
        self.pasta_backups.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(caminho_incompleto, "w") as zip_arquivo:
            zip_arquivo.writestr("banco.db", b"conteudo falso")
            zip_arquivo.writestr("acervo/notas/1.md", "nota")

        validacao = self.backup_service.validar_integridade(caminho_incompleto)

        self.assertFalse(validacao.valido)
        self.assertIn("vetores", validacao.componentes_ausentes)

    def test_validar_integridade_rejeita_arquivo_corrompido(self) -> None:
        caminho_corrompido = self.pasta_backups / "wds_backup_corrompido.zip"
        self.pasta_backups.mkdir(parents=True, exist_ok=True)
        caminho_corrompido.write_bytes(b"isto nao e um zip valido")

        validacao = self.backup_service.validar_integridade(caminho_corrompido)

        self.assertFalse(validacao.valido)
        self.assertIn("corrompido", validacao.mensagem_erro.lower())

    def test_validar_integridade_rejeita_arquivo_inexistente(self) -> None:
        validacao = self.backup_service.validar_integridade(
            self.pasta_backups / "nao_existe.zip"
        )

        self.assertFalse(validacao.valido)
        self.assertIn("nao encontrado", validacao.mensagem_erro.lower())

    # -- Restauracao ----------------------------------------------------

    def test_restaurar_backup_recupera_estado_anterior_de_verdade(self) -> None:
        """Round-trip completo: cria dados, faz backup, destroi os dados
        atuais, restaura, e confirma que o estado restaurado bate
        exatamente com o que existia no momento do backup."""
        objeto_original = self._criar_nota("Nota original", "texto original")
        resultado_backup = self.backup_service.criar_backup()
        self.assertTrue(resultado_backup.sucesso)

        caminho_nota_original = Path(objeto_original.caminho)
        texto_no_backup = caminho_nota_original.read_text(encoding="utf-8")

        # Simula perda de dados: apaga banco, acervo e vetores.
        self.caminho_banco.unlink()
        import shutil

        shutil.rmtree(self.pasta_acervo)
        shutil.rmtree(self.pasta_vetores)

        resultado_restauracao = self.backup_service.restaurar_backup(
            resultado_backup.caminho
        )

        self.assertTrue(resultado_restauracao.sucesso, resultado_restauracao.mensagem_erro)
        self.assertTrue(self.caminho_banco.is_file())
        self.assertTrue(caminho_nota_original.is_file())
        self.assertEqual(
            caminho_nota_original.read_text(encoding="utf-8"), texto_no_backup
        )
        self.assertTrue((self.pasta_vetores / "chroma.sqlite3").is_file())

        # O banco restaurado precisa ser consultavel de verdade, nao so
        # um arquivo com o nome certo.
        objeto_service_novo = ObjetoService(Database(self.caminho_banco))
        objeto_recuperado = objeto_service_novo.obter_por_id(objeto_original.id)
        self.assertEqual(objeto_recuperado.titulo, "Nota original")

    def test_restaurar_backup_recusa_backup_incompleto_sem_alterar_nada(self) -> None:
        self._criar_nota("Nota que deve permanecer", "conteudo original")
        caminho_incompleto = self.pasta_backups / "wds_backup_incompleto.zip"
        self.pasta_backups.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(caminho_incompleto, "w") as zip_arquivo:
            zip_arquivo.writestr("banco.db", b"conteudo falso")

        conteudo_banco_antes = self.caminho_banco.read_bytes()

        resultado = self.backup_service.restaurar_backup(caminho_incompleto)

        self.assertFalse(resultado.sucesso)
        self.assertIn("incompleto", resultado.mensagem_erro.lower())
        # Nada foi tocado -- o banco original continua intacto.
        self.assertEqual(self.caminho_banco.read_bytes(), conteudo_banco_antes)

    def test_restaurar_backup_reverte_em_caso_de_falha_no_meio_do_processo(self) -> None:
        """Se a extracao falhar depois que acervo/vetores ja foram
        removidos, o estado anterior precisa ser recuperado -- o
        usuario nunca pode ficar com um acervo pela metade."""
        objeto_original = self._criar_nota("Nota que nao pode sumir", "texto")
        resultado_backup = self.backup_service.criar_backup()
        caminho_nota_original = Path(objeto_original.caminho)
        texto_original = caminho_nota_original.read_text(encoding="utf-8")

        with patch(
            "services.backup_service.shutil.move",
            side_effect=OSError("falha simulada de disco"),
        ):
            resultado = self.backup_service.restaurar_backup(resultado_backup.caminho)

        self.assertFalse(resultado.sucesso)
        self.assertIn("recuperado", resultado.mensagem_erro.lower())
        # O estado anterior precisa ter sido restaurado de verdade.
        self.assertTrue(self.caminho_banco.is_file())
        self.assertTrue(caminho_nota_original.is_file())
        self.assertEqual(
            caminho_nota_original.read_text(encoding="utf-8"), texto_original
        )


if __name__ == "__main__":
    unittest.main()
