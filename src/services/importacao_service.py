"""Servico responsavel pela importacao de arquivos para o Acervo.

Garante o calculo de hash para deteccao de duplicatas e a coordenacao
do processamento de extracao de textos e arquivos fisicos.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from pypdf import PdfReader

from models import Objeto
from services.acervo_service import AcervoService


DEFAULT_PASTA_PDFS = Path(__file__).resolve().parents[2] / "acervo" / "pdfs"
DEFAULT_PASTA_NOTAS = Path(__file__).resolve().parents[2] / "acervo" / "notas"


class DuplicataError(Exception):
    """Excecao lancada quando um arquivo ja existe no acervo."""


class ImportacaoService:
    """Orquestra a importacao de arquivos fisicos para o Acervo.

    Depende de AcervoService (nao de ObjetoService diretamente) para que
    todo arquivo importado seja automaticamente indexado para busca
    semantica, do mesmo modo que qualquer outro cadastro no sistema.
    """

    def __init__(
        self,
        acervo_service: AcervoService,
        pasta_pdfs: Path | str = DEFAULT_PASTA_PDFS,
        pasta_notas: Path | str = DEFAULT_PASTA_NOTAS,
    ) -> None:
        self._acervo_service = acervo_service
        self._pasta_pdfs = Path(pasta_pdfs)
        self._pasta_notas = Path(pasta_notas)

    def calcular_hash(self, caminho_arquivo: str | Path) -> str:
        """Calcula o hash SHA-256 do conteudo de um arquivo fisico."""
        caminho = Path(caminho_arquivo)
        if not caminho.is_file():
            raise FileNotFoundError(f"Arquivo nao encontrado: {caminho}")

        sha256 = hashlib.sha256()
        with open(caminho, "rb") as arquivo:
            # Le em blocos para nao estourar a memoria com arquivos grandes
            for bloco in iter(lambda: arquivo.read(4096), b""):
                sha256.update(bloco)

        return sha256.hexdigest()

    def verificar_duplicata(self, hash_arquivo: str) -> None:
        """Verifica se um hash ja esta associado a um Objeto ativo no acervo.

        Objetos na lixeira nao contam como duplicata -- ver
        docs/arquitetura.md, secao "Deteccao de Duplicatas".
        """
        for objeto in self._acervo_service.listar_ativos():
            if objeto.hash_arquivo == hash_arquivo:
                raise DuplicataError(
                    f"O arquivo ja esta no acervo (Objeto ID: {objeto.id})."
                )

    def extrair_texto_pdf(self, caminho_arquivo: str | Path) -> str:
        """Extrai o texto de todas as paginas de um PDF.

        Paginas sem texto extraivel (por exemplo, paginas somente-imagem
        sem OCR) contribuem com string vazia, sem interromper a extracao
        das demais paginas do documento.
        """
        leitor = PdfReader(str(caminho_arquivo))
        paginas = [pagina.extract_text() or "" for pagina in leitor.pages]
        return "\n\n".join(paginas).strip()

    def importar_pdf(
        self,
        caminho_arquivo: str | Path,
        *,
        titulo: str | None = None,
        resumo: str | None = None,
    ) -> Objeto:
        """Importa um arquivo PDF para o Acervo.

        Fluxo:
        1. calcula o hash do arquivo original e verifica duplicata;
        2. extrai o texto do PDF (usado como resumo pesquisavel), a
           menos que um resumo explicito seja fornecido;
        3. cadastra o objeto via AcervoService, o que garante a
           indexacao semantica automatica;
        4. copia o arquivo fisico para acervo/pdfs/{id}.pdf -- o nome
           fisico nunca usa o titulo, apenas o ID (AGENTS.md, secao
           "Arquivos do Usuario");
        5. atualiza o objeto com o caminho definitivo do arquivo.

        Se qualquer etapa apos o cadastro falhar (por exemplo, erro ao
        copiar o arquivo), o objeto recem-criado e removido em cascade,
        para nao deixar registros orfaos sem arquivo fisico associado.
        """
        caminho_original = Path(caminho_arquivo)
        if not caminho_original.is_file():
            raise FileNotFoundError(f"Arquivo nao encontrado: {caminho_original}")

        hash_arquivo = self.calcular_hash(caminho_original)
        self.verificar_duplicata(hash_arquivo)

        resumo_final = (
            resumo if resumo is not None else self.extrair_texto_pdf(caminho_original)
        )
        titulo_final = titulo if titulo is not None else caminho_original.stem

        objeto = self._acervo_service.cadastrar(
            titulo_final,
            "PDF",
            resumo=resumo_final,
            hash_arquivo=hash_arquivo,
        )

        try:
            self._pasta_pdfs.mkdir(parents=True, exist_ok=True)
            caminho_definitivo = self._pasta_pdfs / f"{objeto.id}.pdf"
            shutil.copy2(caminho_original, caminho_definitivo)
        except Exception:
            self._acervo_service.excluir(objeto.id)
            self._acervo_service.excluir_definitivamente(objeto.id)
            raise

        return self._acervo_service.atualizar(
            objeto.id,
            titulo_final,
            "PDF",
            caminho=str(caminho_definitivo),
        )

    def importar_markdown(
        self,
        caminho_arquivo: str | Path,
        *,
        titulo: str | None = None,
        resumo: str | None = None,
    ) -> Objeto:
        """Importa um arquivo Markdown para o Acervo.

        Fluxo:
        1. calcula o hash do arquivo original e verifica duplicata;
        2. le o conteudo do arquivo como texto puro (usado como resumo
           pesquisavel), a menos que um resumo explicito seja
           fornecido -- diferente do PDF, Markdown ja e texto, entao
           nao ha etapa de extracao separada;
        3. cadastra o objeto via AcervoService, o que garante a
           indexacao semantica automatica;
        4. copia o arquivo fisico para acervo/notas/{id}.md -- o nome
           fisico nunca usa o titulo, apenas o ID (AGENTS.md, secao
           "Arquivos do Usuario");
        5. atualiza o objeto com o caminho definitivo do arquivo.

        Se qualquer etapa apos o cadastro falhar, o objeto recem-criado
        e removido em cascade, para nao deixar registros orfaos sem
        arquivo fisico associado -- mesmo comportamento de
        importar_pdf.
        """
        caminho_original = Path(caminho_arquivo)
        if not caminho_original.is_file():
            raise FileNotFoundError(f"Arquivo nao encontrado: {caminho_original}")

        hash_arquivo = self.calcular_hash(caminho_original)
        self.verificar_duplicata(hash_arquivo)

        resumo_final = (
            resumo
            if resumo is not None
            else caminho_original.read_text(encoding="utf-8")
        )
        titulo_final = titulo if titulo is not None else caminho_original.stem

        objeto = self._acervo_service.cadastrar(
            titulo_final,
            "Markdown",
            resumo=resumo_final,
            hash_arquivo=hash_arquivo,
        )

        try:
            self._pasta_notas.mkdir(parents=True, exist_ok=True)
            caminho_definitivo = self._pasta_notas / f"{objeto.id}.md"
            shutil.copy2(caminho_original, caminho_definitivo)
        except Exception:
            self._acervo_service.excluir(objeto.id)
            self._acervo_service.excluir_definitivamente(objeto.id)
            raise

        return self._acervo_service.atualizar(
            objeto.id,
            titulo_final,
            "Markdown",
            caminho=str(caminho_definitivo),
        )

    def cadastrar_link(
        self,
        url: str,
        *,
        titulo: str | None = None,
        resumo: str | None = None,
    ) -> Objeto:
        """Cadastra um link (URL) no Acervo.

        Diferente de PDFs e Markdown, um link nao possui arquivo fisico
        nem conteudo para calcular hash -- a deteccao de duplicata e
        feita comparando diretamente a URL entre os objetos ativos, nao
        pelo hash de um arquivo.

        Nao busca automaticamente titulo ou descricao da pagina, pois
        isso exigiria uma requisicao web e fica fora do escopo deste
        incremento. Se nenhum titulo for fornecido, a propria URL e
        usada como titulo.
        """
        url = url.strip()
        if not url:
            raise ValueError("A URL nao pode ser vazia.")

        self._verificar_link_duplicado(url)

        titulo_final = titulo if titulo is not None else url

        return self._acervo_service.cadastrar(
            titulo_final,
            "Link",
            caminho=url,
            resumo=resumo,
        )

    def _verificar_link_duplicado(self, url: str) -> None:
        """Verifica se a URL ja esta cadastrada em um Objeto ativo.

        Objetos na lixeira nao contam como duplicata, pelo mesmo
        motivo documentado para arquivos em docs/arquitetura.md, secao
        "Deteccao de Duplicatas".
        """
        for objeto in self._acervo_service.listar_ativos():
            if objeto.caminho == url:
                raise DuplicataError(
                    f"Este link ja esta no acervo (Objeto ID: {objeto.id})."
                )

    def criar_nota_manual(
        self,
        titulo: str,
        conteudo: str = "",
    ) -> Objeto:
        """Cria uma Nota digitada manualmente pelo usuario.

        Salva o conteudo imediatamente como arquivo fisico em
        acervo/notas/{id}.md -- igual a uma nota importada, para que o
        Editor Markdown sempre edite um arquivo real, nunca um estado
        que existe somente no banco (decisao registrada em
        docs/interface-grafica.md, secao Editor Markdown).

        Diferente de importar_markdown, nao ha arquivo de origem nem
        hash para verificar duplicata -- cada nota manual nasce unica,
        vazia ou com o conteudo inicial fornecido.
        """
        if not titulo.strip():
            raise ValueError("O titulo nao pode ser vazio.")

        objeto = self._acervo_service.cadastrar(titulo, "Nota", resumo=conteudo)

        try:
            self._pasta_notas.mkdir(parents=True, exist_ok=True)
            caminho_definitivo = self._pasta_notas / f"{objeto.id}.md"
            caminho_definitivo.write_text(conteudo, encoding="utf-8")
        except Exception:
            self._acervo_service.excluir(objeto.id)
            self._acervo_service.excluir_definitivamente(objeto.id)
            raise

        return self._acervo_service.atualizar(
            objeto.id,
            titulo,
            "Nota",
            caminho=str(caminho_definitivo),
        )
