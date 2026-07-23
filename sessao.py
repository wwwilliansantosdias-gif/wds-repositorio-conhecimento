"""Carrega os servicos do WDS para uso interativo no Python.

Uso:
    python -i sessao.py

O -i mantem o Python aberto depois de rodar este arquivo, com o
AcervoService (acervo) ja disponivel -- ele cadastra e indexa para
busca semantica automaticamente, em uma unica chamada. Os servicos
individuais (objetos, tags, relacoes, pesquisa, embeddings) tambem
continuam disponiveis para uso avancado ou depuracao.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from persistence import Database
from services.acervo_service import AcervoService
from services.embedding_service import EmbeddingService
from services.objeto_service import ObjetoService
from services.pesquisa_service import PesquisaService
from services.relacao_service import RelacaoService
from services.tag_service import TagService

print("Carregando banco de dados e servicos do WDS...")

db = Database()
db.initialize()

objetos = ObjetoService(db)
tags = TagService(db)
relacoes = RelacaoService(db)
pesquisa = PesquisaService(db)
embeddings = EmbeddingService(db)
acervo = AcervoService(objetos, embeddings)

print("Pronto! Disponivel: acervo (recomendado), alem de objetos, tags,")
print("relacoes, pesquisa e embeddings para uso avancado.")
print()
print("Exemplo (cadastra e ja indexa para busca semantica):")
print("  obj = acervo.cadastrar(titulo='Teste', tipo='Nota', resumo='...')")
print("  tags.criar('minha-tag')")
print("  for item, score in embeddings.buscar_semantico('algum tema'):")
print("      print(score, item.titulo)")
