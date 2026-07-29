# Backlog do Projeto

Este documento define todas as Issues planejadas para o desenvolvimento.

As Issues devem ser implementadas na ordem apresentada.

Nenhuma Issue deve alterar a arquitetura definida em
docs/arquitetura.md.

---

# Progresso Geral

O Dashboard foi adiado para versao posterior ao MVP v1.0.0. As demais
issues do MVP foram concluÃ­das e validadas para a release.

| Fase | Status |
|---|---|
| 1 -- Fundacao | Concluida |
| 2 -- Persistencia | Concluida |
| 3 -- Modelo de Dominio | Concluida |
| 4 -- Servicos | Concluida |
| 5 -- Pesquisa | Concluida |
| 6 -- Importacao | Concluida |
| 7 -- Interface Grafica | Concluida (Dashboard adiado para versao posterior ao MVP) |
| 8 -- Backup e Recuperacao | Concluida |
| 9 -- Testes e Validacao | Concluida |
| 10 -- Release 1.0 | Em andamento (empacotamento Windows em preparacao) |

---

# EPIC 1 â€” FundaÃ§Ã£o

## Issue 1

TÃ­tulo

Estrutura inicial do projeto

Objetivo

Criar a estrutura de diretÃ³rios.

CritÃ©rios de aceitaÃ§Ã£o

- criar src
- criar tests
- criar docs
- criar assets
- criar acervo
- criar backups
- criar vetores

Status

Concluida

---

## Issue 2

TÃ­tulo

ConfiguraÃ§Ã£o do ambiente Python

Objetivo

Criar o ambiente base.

CritÃ©rios

- pyproject.toml
- requirements.txt
- .gitignore

Status

Concluida

---

## Issue 3

TÃ­tulo

InicializaÃ§Ã£o da aplicaÃ§Ã£o

Objetivo

Criar app.py.

CritÃ©rios

AplicaÃ§Ã£o abre sem erros.

Status

Concluida

---

# EPIC 2 â€” Banco

## Issue 4

TÃ­tulo

Criar banco SQLite

CritÃ©rios

- banco.db
- conexÃ£o
- criaÃ§Ã£o automÃ¡tica

Status

Concluida

---

## Issue 5

TÃ­tulo

Criar tabela_objetos

Status

Concluida

---

## Issue 6

TÃ­tulo

Criar tabela_tags

Status

Concluida

---

## Issue 7

TÃ­tulo

Criar tabela_objeto_tag

Status

Concluida

---

## Issue 8

TÃ­tulo

Criar tabela_relacoes

Status

Concluida

---

# EPIC 3 â€” Modelos

## Issue 9

Modelo Objeto

Status

Concluida

---

## Issue 10

Modelo Tag

Status

Concluida

---

## Issue 11

Modelo RelaÃ§Ã£o

Status

Concluida

---

# EPIC 4 â€” ServiÃ§os

## Issue 12

CRUD de Objetos

Status

ConcluÃ­da

---

## Issue 13

CRUD de Tags

Status

ConcluÃ­da

---

## Issue 14

Relacionamentos

Status

ConcluÃ­da

---

## Issue 15

Lixeira

Status

ConcluÃ­da

---

# EPIC 5 â€” Pesquisa

## Issue 16

SQLite FTS5

Status

Concluida

---

## Issue 17

Pesquisa textual

Status

Concluida

---

## Issue 18

IntegraÃ§Ã£o ChromaDB

Status

Concluida

---

## Issue 19

Busca por significado

Status

Concluida

ObservaÃ§Ã£o: inclui a sincronia automatica entre cadastro/atualizacao/
exclusao de objetos e o indice semantico, via AcervoService (nao
formalizado como Issue separada no backlog original).

---

# EPIC 6 â€” ImportaÃ§Ã£o

## Issue 19b

DetecÃ§Ã£o de duplicatas (fundaÃ§Ã£o)

Objetivo

Calcular hash SHA-256 de um arquivo e impedir a importacao de arquivos
ja presentes no acervo.

Status

Concluida (base implementada em ImportacaoService; ainda nao integrada
ao fluxo completo de importacao)

---

## Issue 20

ImportaÃ§Ã£o de PDFs

Status

Concluida

---

## Issue 21

ImportaÃ§Ã£o de Markdown

Status

Concluida

---

## Issue 22

ImportaÃ§Ã£o de Links

Status

Concluida

---

## Issue 22b

ImportaÃ§Ã£o de Docx

Objetivo

Extrair texto de documentos .docx (via python-docx) e importa-los para
o Acervo, seguindo exatamente o mesmo fluxo ja usado por
importar_pdf/importar_markdown (hash, deteccao de duplicata,
indexacao automatica, copia fisica pelo ID em acervo/documentos/).

Usa o tipo "Documento" (nao "Docx"), pensado para acomodar outros
formatos de documento de texto no futuro sem multiplicar tipos por
extensao.

Status

Concluida (nao fazia parte do escopo original da Fase 6, mas foi
adicionada por ter complexidade baixa e reaproveitar 100% do padrao ja
testado de importar_pdf -- ver docs/arquitetura.md, "a mÃ­dia Ã© apenas
uma caracterÃ­stica do objeto")

---

# EPIC 7 â€” Interface

## Issue 23

Dashboard

Status

Adiada para versao posterior ao MVP v1.0.0.

---

## Issue 24

Biblioteca

Status

Concluida

ObservaÃ§Ã£o: nao virou uma tela/janela nova -- reaproveita literalmente
o mesmo componente de lista da area de Resultados (ResultadoItem),
conforme "Utiliza os mesmos componentes da pesquisa"
(docs/interface-grafica.md). `PesquisaController.listar_todos()` lista
os objetos ativos (via AcervoService), mais recente primeiro, sem
score (nao ha termo de busca para medir relevancia). Acionada por um
botao "Biblioteca" na Barra Superior; a pesquisa continua funcionando
normalmente depois, sem que a Biblioteca deixe nenhum estado residual.

---

## Issue 25

Pesquisa

Status

Concluida (SearchBar na Barra Superior, PesquisaView renderiza os
resultados via PesquisaController -- ja implementado e coberto por
tests/test_pesquisa_controller.py antes desta sessao; o Status aqui
estava desatualizado)

---

## Issue 26

Editor Markdown

Status

Concluida

ObservaÃ§Ã£o: implementado como janela modal (`EditorMarkdownWindow`,
`ctk.CTkToplevel`), seguindo o mesmo padrÃ£o jÃ¡ usado pela Lixeira, em
vez de um frame embutido na janela principal. Acionado pelo botÃ£o
"Editar" em Objeto em Foco, visÃ­vel apenas para tipos editÃ¡veis
(`Nota`/`Markdown`). Ao salvar, o painel de Objeto em Foco Ã©
atualizado automaticamente; ao fechar com alteraÃ§Ãµes nÃ£o salvas, pede
confirmaÃ§Ã£o antes de descartar. Sem realce de sintaxe ou
prÃ©-visualizaÃ§Ã£o, conforme decidido ("nÃ£o pretende substituir editores
especializados").

---

## Issue 27

ConfiguraÃ§Ãµes

Status

Concluida

ObservaÃ§Ã£o: o escopo nao estava definido em nenhum documento (so
havia "Centraliza as configuraÃ§Ãµes do sistema" e um config.json vazio
nunca lido por ninguem). Decisao tomada aqui: comecar com apenas duas
preferencias, as unicas coisas hoje hardcoded no codigo que fazem
sentido como preferencia pessoal sem mexer em nada estrutural --
tema da interface (Sistema/Claro/Escuro, aplicado imediatamente via
`ctk.set_appearance_mode`) e quantidade de resultados semanticos por
busca (`PesquisaController`, antes fixo em 10). Implementado como
`ConfigService` (le/escreve `config.json` com escrita atomica e
defaults seguros -- nunca falha por causa de um arquivo ausente,
corrompido ou desatualizado) + `ConfiguracoesWindow`, janela modal no
mesmo padrao de Lixeira/Backup/Editor Markdown. Mudar o local de
armazenamento dos dados (acervo/vetores/banco) ficou de fora por ser
uma decisao maior, que afeta o Backup inteiro -- fica para quando for
decidida explicitamente.

---

# EPIC 8 â€” Backup

## Issue 28

Backup

Status

Concluida

ObservaÃ§Ã£o: implementado como `BackupService.criar_backup()`, gerando
um unico arquivo .zip autocontido (`backups/wds_backup_AAAAMMDD_HHMMSS.zip`)
com banco.db + acervo/ + vetores/ juntos -- nunca uma copia solta dos
tres, para nao permitir um backup parcial por engano
(docs/arquitetura.md, seÃ§Ã£o "Backup"). O banco.db e copiado via
`sqlite3.Connection.backup()`, nao por copia de arquivo bruta, para
garantir uma copia consistente mesmo que outra conexao esteja
escrevendo no momento.

CorreÃ§Ã£o associada: o caminho padrÃ£o do Ã­ndice ChromaDB no cÃ³digo era
`chroma_db/`, divergente do `vetores/` jÃ¡ documentado em
docs/arquitetura.md (e jÃ¡ com `.gitkeep` reservado no repositÃ³rio).
Corrigido em `embedding_service.py` para usar `vetores/`, conforme
AGENTS.md ("em caso de conflito, a arquitetura sempre prevalece").
Quem jÃ¡ tinha uma pasta `chroma_db/` local com embeddings reais
precisa renomeÃ¡-la para `vetores/` para nÃ£o perder o Ã­ndice.

---

## Issue 29

RestauraÃ§Ã£o

Status

Concluida

ObservaÃ§Ã£o: `BackupService.restaurar_backup()` recusa backups
incompletos antes de tocar em qualquer arquivo (via
`validar_integridade()`), guarda uma copia de seguranca do estado
atual antes de sobrescrever, e reverte automaticamente para essa copia
se qualquer etapa da extracao falhar no meio do processo -- testado
com um teste que forca uma falha real de disco a meio caminho e
confirma que nada se perde. Acessivel pela tela "Backup" (botao na
Barra Superior), que lista os backups existentes com opcao de
restaurar cada um. Exige reiniciar o WDS apos restaurar, ja que
objetos em memoria (conexao do ChromaDB, cache dos Services) nao sao
recarregados automaticamente -- decisao deliberada para manter o
escopo simples, documentada no proprio codigo.

---

# EPIC 9 â€” Testes

## Issue 30

Testes UnitÃ¡rios

Status

Concluida na validacao da release v1.0.0.

---

## Issue 31

Testes de IntegraÃ§Ã£o

Status

Concluida na validacao da release v1.0.0, incluindo
`tests/test_integracao_acervo.py`.

---

# EPIC 10 â€” Release

## Issue 32

VersÃ£o 1.0

Status

Em andamento: documentação revisada.`r`n