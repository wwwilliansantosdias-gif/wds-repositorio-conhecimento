"""Testes do Servico de Importacao (Fase 6)."""

from __future__ import annotations

import base64
import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile, TemporaryDirectory
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from persistence import Database
from services.acervo_service import AcervoService
from services.embedding_service import EmbeddingService
from services.importacao_service import DuplicataError, ImportacaoService
from services.objeto_service import ObjetoService

from docx import Document as DocumentoDocx


# PDF real (gerado com reportlab), contendo o texto:
# "Ensaio sobre estoicismo" / "Reflexao sobre o pensamento filosofico de Epicteto."
# Codificado em base64 para nao depender de bibliotecas externas nos testes.
PDF_TESTE_BASE64 = (
    "JVBERi0xLjMKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgKG9wZW5zb3VyY2UpCjEgMCBvYmoKPDwKL0YxIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9CYXNlRm9udCAvSGVsdmV0aWNhIC9FbmNvZGluZyAvV2luQW5zaUVuY29kaW5nIC9OYW1lIC9GMSAvU3VidHlwZSAvVHlwZTEgL1R5cGUgL0ZvbnQKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL0NvbnRlbnRzIDcgMCBSIC9NZWRpYUJveCBbIDAgMCA1OTUuMjc1NiA4NDEuODg5OCBdIC9QYXJlbnQgNiAwIFIgL1Jlc291cmNlcyA8PAovRm9udCAxIDAgUiAvUHJvY1NldCBbIC9QREYgL1RleHQgL0ltYWdlQiAvSW1hZ2VDIC9JbWFnZUkgXQo+PiAvUm90YXRlIDAgL1RyYW5zIDw8Cgo+PiAKICAvVHlwZSAvUGFnZQo+PgplbmRvYmoKNCAwIG9iago8PAovUGFnZU1vZGUgL1VzZU5vbmUgL1BhZ2VzIDYgMCBSIC9UeXBlIC9DYXRhbG9nCj4+CmVuZG9iago1IDAgb2JqCjw8Ci9BdXRob3IgKGFub255bW91cykgL0NyZWF0aW9uRGF0ZSAoRDoyMDI2MDcyMzAyMjg1MCswMCcwMCcpIC9DcmVhdG9yIChhbm9ueW1vdXMpIC9LZXl3b3JkcyAoKSAvTW9kRGF0ZSAoRDoyMDI2MDcyMzAyMjg1MCswMCcwMCcpIC9Qcm9kdWNlciAoUmVwb3J0TGFiIFBERiBMaWJyYXJ5IC0gXChvcGVuc291cmNlXCkpIAogIC9TdWJqZWN0ICh1bnNwZWNpZmllZCkgL1RpdGxlICh1bnRpdGxlZCkgL1RyYXBwZWQgL0ZhbHNlCj4+CmVuZG9iago2IDAgb2JqCjw8Ci9Db3VudCAxIC9LaWRzIFsgMyAwIFIgXSAvVHlwZSAvUGFnZXMKPj4KZW5kb2JqCjcgMCBvYmoKPDwKL0ZpbHRlciBbIC9BU0NJSTg1RGVjb2RlIC9GbGF0ZURlY29kZSBdIC9MZW5ndGggMTY5Cj4+CnN0cmVhbQpHYXJXMFltUz81JjRIRENgS1kqTEReQWpHUzxbKywrLEspJFhRNloxR0QyW1gmSlpqLUAjQUNMLEllWHE0IWBiLmZPIm8rIShUbDtHMk9sNTJnKSVFUSg1YlZrZUlLRDVOUDA/Zmt1XjVFXFMjbFBBUyxIbkVxQ15oSSYhVlBpcU8pJUM5IzZQLFQ6bU5nOzgzMFxjaFxla2kvRXFdZVEkIWU0UTNxWn4+ZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgOAowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwNjEgMDAwMDAgbiAKMDAwMDAwMDA5MiAwMDAwMCBuIAowMDAwMDAwMTk5IDAwMDAwIG4gCjAwMDAwMDA0MDIgMDAwMDAgbiAKMDAwMDAwMDQ3MCAwMDAwMCBuIAowMDAwMDAwNzMxIDAwMDAwIG4gCjAwMDAwMDA3OTAgMDAwMDAgbiAKdHJhaWxlcgo8PAovSUQgCls8MDU4ZjQ0NTRhODE4NzBiMWRjNGJjODBmMjcyN2FkMzk+PDA1OGY0NDU0YTgxODcwYjFkYzRiYzgwZjI3MjdhZDM5Pl0KJSBSZXBvcnRMYWIgZ2VuZXJhdGVkIFBERiBkb2N1bWVudCAtLSBkaWdlc3QgKG9wZW5zb3VyY2UpCgovSW5mbyA1IDAgUgovUm9vdCA0IDAgUgovU2l6ZSA4Cj4+CnN0YXJ0eHJlZgoxMDQ5CiUlRU9GCg=="
)


class ImportacaoServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        temporary_path = Path(self.temporary_directory.name)

        self.database = Database(temporary_path / "banco.db")
        self.database.initialize()

        self.objeto_service = ObjetoService(self.database)
        self.embedding_service = EmbeddingService(
            self.database,
            chroma_path=temporary_path / "chroma_db",
        )
        self.acervo_service = AcervoService(self.objeto_service, self.embedding_service)

        self.pasta_pdfs = temporary_path / "acervo" / "pdfs"
        self.pasta_notas = temporary_path / "acervo" / "notas"
        self.pasta_documentos = temporary_path / "acervo" / "documentos"
        self.importacao_service = ImportacaoService(
            self.acervo_service,
            pasta_pdfs=self.pasta_pdfs,
            pasta_notas=self.pasta_notas,
            pasta_documentos=self.pasta_documentos,
        )

        self.pdf_path = temporary_path / "documento_original.pdf"
        self.pdf_path.write_bytes(base64.b64decode(PDF_TESTE_BASE64))

        self.markdown_path = temporary_path / "anotacao_original.md"
        self.markdown_path.write_text(
            "# Ensaio sobre estoicismo\n\n"
            "Reflexao sobre o pensamento filosofico de Epicteto.",
            encoding="utf-8",
        )

        self.docx_path = temporary_path / "relatorio_original.docx"
        documento_docx = DocumentoDocx()
        documento_docx.add_paragraph("Ensaio sobre estoicismo")
        documento_docx.add_paragraph(
            "Reflexao sobre o pensamento filosofico de Epicteto."
        )
        documento_docx.save(str(self.docx_path))

    def tearDown(self) -> None:
        del self.embedding_service
        try:
            self.temporary_directory.cleanup()
        except PermissionError:
            # O ChromaDB pode manter arquivos temporarios abertos no Windows.
            pass

    def test_calcular_hash_gera_sha256_correto_para_arquivo(self) -> None:
        conteudo = b"Conteudo de teste para hash"
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(conteudo)
            temp_path = temp_file.name

        try:
            hash_gerado = self.importacao_service.calcular_hash(temp_path)
            self.assertEqual(
                hash_gerado,
                "a1dd6544a87445346439572db643b9e95683a40565bb661026b369aaa44bf101",
            )
        finally:
            os.remove(temp_path)

    def test_verificar_duplicata_lanca_excecao_se_hash_ja_existir(self) -> None:
        hash_teste = "hash-duplicado-123"
        self.objeto_service.cadastrar(
            "Arquivo Existente",
            "PDF",
            hash_arquivo=hash_teste,
        )

        with self.assertRaises(DuplicataError):
            self.importacao_service.verificar_duplicata(hash_teste)

    def test_verificar_duplicata_ignora_objetos_na_lixeira(self) -> None:
        hash_teste = "hash-na-lixeira-456"
        objeto = self.objeto_service.cadastrar(
            "Arquivo Excluido",
            "PDF",
            hash_arquivo=hash_teste,
        )
        self.objeto_service.excluir(objeto.id)

        # Nao deve lancar excecao: objeto na lixeira nao conta como duplicata.
        self.importacao_service.verificar_duplicata(hash_teste)

    def test_verificar_duplicata_passa_silenciosamente_se_hash_for_novo(self) -> None:
        hash_teste = "hash-novo-123"
        self.importacao_service.verificar_duplicata(hash_teste)

    def test_extrair_texto_pdf_retorna_conteudo_real_do_documento(self) -> None:
        texto = self.importacao_service.extrair_texto_pdf(self.pdf_path)

        self.assertIn("Ensaio sobre estoicismo", texto)
        self.assertIn("Epicteto", texto)

    def test_importar_pdf_cadastra_copia_e_indexa_o_objeto(self) -> None:
        objeto = self.importacao_service.importar_pdf(self.pdf_path)

        self.assertEqual(objeto.titulo, "documento_original")
        self.assertEqual(objeto.tipo, "PDF")
        self.assertIn("Ensaio sobre estoicismo", objeto.resumo)
        self.assertIsNotNone(objeto.hash_arquivo)

        caminho_copiado = self.pasta_pdfs / f"{objeto.id}.pdf"
        self.assertTrue(caminho_copiado.is_file())
        self.assertEqual(objeto.caminho, str(caminho_copiado))

        encontrados = self.embedding_service.buscar_semantico(
            "aceitacao estoica do sofrimento"
        )
        self.assertTrue(any(item.id == objeto.id for item, _ in encontrados))

    def test_importar_pdf_usa_titulo_explicito_quando_fornecido(self) -> None:
        objeto = self.importacao_service.importar_pdf(
            self.pdf_path,
            titulo="Meu titulo customizado",
        )

        self.assertEqual(objeto.titulo, "Meu titulo customizado")

    def test_importar_pdf_impede_duplicata(self) -> None:
        self.importacao_service.importar_pdf(self.pdf_path)

        with self.assertRaises(DuplicataError):
            self.importacao_service.importar_pdf(self.pdf_path)

    def test_importar_pdf_arquivo_inexistente_leva_a_erro_claro(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.importacao_service.importar_pdf("caminho/que/nao/existe.pdf")

    def test_importar_markdown_cadastra_copia_e_indexa_o_objeto(self) -> None:
        objeto = self.importacao_service.importar_markdown(self.markdown_path)

        self.assertEqual(objeto.titulo, "anotacao_original")
        self.assertEqual(objeto.tipo, "Markdown")
        self.assertIn("Ensaio sobre estoicismo", objeto.resumo)
        self.assertIsNotNone(objeto.hash_arquivo)

        caminho_copiado = self.pasta_notas / f"{objeto.id}.md"
        self.assertTrue(caminho_copiado.is_file())
        self.assertEqual(objeto.caminho, str(caminho_copiado))

        encontrados = self.embedding_service.buscar_semantico(
            "aceitacao estoica do sofrimento"
        )
        self.assertTrue(any(item.id == objeto.id for item, _ in encontrados))

    def test_importar_markdown_usa_titulo_explicito_quando_fornecido(self) -> None:
        objeto = self.importacao_service.importar_markdown(
            self.markdown_path,
            titulo="Meu titulo customizado",
        )

        self.assertEqual(objeto.titulo, "Meu titulo customizado")

    def test_importar_markdown_impede_duplicata(self) -> None:
        self.importacao_service.importar_markdown(self.markdown_path)

        with self.assertRaises(DuplicataError):
            self.importacao_service.importar_markdown(self.markdown_path)

    def test_importar_markdown_arquivo_inexistente_leva_a_erro_claro(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.importacao_service.importar_markdown("caminho/que/nao/existe.md")

    def test_importar_pdf_e_markdown_nao_conflitam_como_duplicata(self) -> None:
        """Hashes de conteudo diferente (PDF vs Markdown) nunca colidem,
        mas o teste tambem confirma que importar um nao bloqueia o outro
        quando os arquivos sao de fato diferentes."""
        objeto_pdf = self.importacao_service.importar_pdf(self.pdf_path)
        objeto_md = self.importacao_service.importar_markdown(self.markdown_path)

        self.assertNotEqual(objeto_pdf.id, objeto_md.id)
        self.assertNotEqual(objeto_pdf.hash_arquivo, objeto_md.hash_arquivo)

    def test_extrair_texto_docx_retorna_conteudo_real_do_documento(self) -> None:
        texto = self.importacao_service.extrair_texto_docx(self.docx_path)

        self.assertIn("Ensaio sobre estoicismo", texto)
        self.assertIn("Epicteto", texto)

    def test_importar_docx_cadastra_copia_e_indexa_o_objeto(self) -> None:
        objeto = self.importacao_service.importar_docx(self.docx_path)

        self.assertEqual(objeto.titulo, "relatorio_original")
        self.assertEqual(objeto.tipo, "Documento")
        self.assertIn("Ensaio sobre estoicismo", objeto.resumo)
        self.assertIsNotNone(objeto.hash_arquivo)

        caminho_copiado = self.pasta_documentos / f"{objeto.id}.docx"
        self.assertTrue(caminho_copiado.is_file())
        self.assertEqual(objeto.caminho, str(caminho_copiado))

        encontrados = self.embedding_service.buscar_semantico(
            "aceitacao estoica do sofrimento"
        )
        self.assertTrue(any(item.id == objeto.id for item, _ in encontrados))

    def test_importar_docx_permanece_apos_reabrir_o_banco(self) -> None:
        objeto = self.importacao_service.importar_docx(self.docx_path)

        for _ in range(3):
            banco_reaberto = Database(self.database.path)
            banco_reaberto.initialize()
            objetos_ativos = ObjetoService(banco_reaberto).listar_ativos()

            self.assertEqual([item.id for item in objetos_ativos], [objeto.id])
            self.assertEqual(objetos_ativos[0].tipo, "Documento")
            self.assertEqual(objetos_ativos[0].caminho, objeto.caminho)
            self.assertTrue(Path(objetos_ativos[0].caminho).is_file())

    def test_importar_docx_usa_titulo_explicito_quando_fornecido(self) -> None:
        objeto = self.importacao_service.importar_docx(
            self.docx_path,
            titulo="Meu titulo customizado",
        )

        self.assertEqual(objeto.titulo, "Meu titulo customizado")

    def test_importar_docx_impede_duplicata(self) -> None:
        self.importacao_service.importar_docx(self.docx_path)

        with self.assertRaises(DuplicataError):
            self.importacao_service.importar_docx(self.docx_path)

    def test_importar_docx_arquivo_inexistente_leva_a_erro_claro(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.importacao_service.importar_docx("caminho/que/nao/existe.docx")

    def test_importar_docx_pdf_e_markdown_nao_conflitam_como_duplicata(self) -> None:
        objeto_pdf = self.importacao_service.importar_pdf(self.pdf_path)
        objeto_md = self.importacao_service.importar_markdown(self.markdown_path)
        objeto_docx = self.importacao_service.importar_docx(self.docx_path)

        ids = {objeto_pdf.id, objeto_md.id, objeto_docx.id}
        hashes = {
            objeto_pdf.hash_arquivo,
            objeto_md.hash_arquivo,
            objeto_docx.hash_arquivo,
        }
        self.assertEqual(len(ids), 3)
        self.assertEqual(len(hashes), 3)

    def test_cadastrar_link_persiste_e_indexa(self) -> None:
        objeto = self.importacao_service.cadastrar_link(
            "https://exemplo.com/artigo-sobre-estoicismo",
            titulo="Artigo sobre estoicismo",
            resumo="Reflexao sobre o pensamento filosofico de Epicteto.",
        )

        self.assertEqual(objeto.tipo, "Link")
        self.assertEqual(objeto.caminho, "https://exemplo.com/artigo-sobre-estoicismo")
        self.assertIsNone(objeto.hash_arquivo)

        encontrados = self.embedding_service.buscar_semantico(
            "aceitacao estoica do sofrimento"
        )
        self.assertTrue(any(item.id == objeto.id for item, _ in encontrados))

    def test_cadastrar_link_usa_url_como_titulo_quando_nao_informado(self) -> None:
        objeto = self.importacao_service.cadastrar_link("https://exemplo.com/pagina")

        self.assertEqual(objeto.titulo, "https://exemplo.com/pagina")

    def test_cadastrar_link_impede_duplicata(self) -> None:
        self.importacao_service.cadastrar_link("https://exemplo.com/repetido")

        with self.assertRaises(DuplicataError):
            self.importacao_service.cadastrar_link("https://exemplo.com/repetido")

    def test_cadastrar_link_ignora_duplicata_na_lixeira(self) -> None:
        objeto = self.importacao_service.cadastrar_link("https://exemplo.com/vai-excluir")
        self.acervo_service.excluir(objeto.id)

        # Nao deve lancar excecao: link na lixeira nao conta como duplicata,
        # mesma regra ja aplicada aos arquivos.
        novo_objeto = self.importacao_service.cadastrar_link(
            "https://exemplo.com/vai-excluir"
        )
        self.assertNotEqual(objeto.id, novo_objeto.id)

    def test_cadastrar_link_rejeita_url_vazia(self) -> None:
        with self.assertRaises(ValueError):
            self.importacao_service.cadastrar_link("   ")


if __name__ == "__main__":
    unittest.main()
