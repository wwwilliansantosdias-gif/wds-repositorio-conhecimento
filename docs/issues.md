# Backlog do Projeto

Este documento define todas as Issues planejadas para o desenvolvimento.

As Issues devem ser implementadas na ordem apresentada.

Nenhuma Issue deve alterar a arquitetura definida em
docs/arquitetura.md.

---

# Progresso Geral

O Dashboard foi adiado para versão posterior ao MVP v1.0.0. As demais
issues do MVP foram concluídas e validadas para a release.

| Fase | Status |
|---|---|
| 1 -- Fundação | Concluída |
| 2 -- Persistência | Concluída |
| 3 -- Modelo de Domínio | Concluída |
| 4 -- Serviços | Concluída |
| 5 -- Pesquisa | Concluída |
| 6 -- Importação | Concluída |
| 7 -- Interface Gráfica | Concluída (Dashboard adiado para versão posterior ao MVP) |
| 8 -- Backup e Recuperação | Concluída |
| 9 -- Testes e Validação | Concluída (162 testes) |
| 10 -- Release 1.0 | Concluída (v1.0.0 taggeada e publicada; sem instalador formal, ver Issue 32) |

---

# EPIC 1 — Fundação

## Issue 1

Título

Estrutura inicial do projeto

Objetivo

Criar a estrutura de diretórios.

Critérios de aceitação

- criar src
- criar tests
- criar docs
- criar assets
- criar acervo
- criar backups
- criar vetores

Status

Concluída

---

## Issue 2

Título

Configuração do ambiente Python

Objetivo

Criar o ambiente base.

Critérios

- pyproject.toml
- requirements.txt
- .gitignore

Status

Concluída

---

## Issue 3

Título

Inicialização da aplicação

Objetivo

Criar app.py.

Critérios

Aplicação abre sem erros.

Status

Concluída

---

# EPIC 2 — Banco

## Issue 4

Título

Criar banco SQLite

Critérios

- banco.db
- conexão
- criação automática

Status

Concluída

---

## Issue 5

Título

Criar tabela_objetos

Status

Concluída

---

## Issue 6

Título

Criar tabela_tags

Status

Concluída

---

## Issue 7

Título

Criar tabela_objeto_tag

Status

Concluída

---

## Issue 8

Título

Criar tabela_relacoes

Status

Concluída

---

# EPIC 3 — Modelos

## Issue 9

Modelo Objeto

Status

Concluída

---

## Issue 10

Modelo Tag

Status

Concluída

---

## Issue 11

Modelo Relação

Status

Concluída

---

# EPIC 4 — Serviços

## Issue 12

CRUD de Objetos

Status

Concluída

---

## Issue 13

CRUD de Tags

Status

Concluída

---

## Issue 14

Relacionamentos

Status

Concluída

---

## Issue 15

Lixeira

Status

Concluída

---

# EPIC 5 — Pesquisa

## Issue 16

SQLite FTS5

Status

Concluída

---

## Issue 17

Pesquisa textual

Status

Concluída

---

## Issue 18

Integração ChromaDB

Status

Concluída

---

## Issue 19

Busca por significado

Status

Concluída

Observação: inclui a sincronia automática entre cadastro/atualização/
exclusão de objetos e o índice semântico, via AcervoService (não
formalizado como Issue separada no backlog original).

---

# EPIC 6 — Importação

## Issue 19b

Detecção de duplicatas (fundação)

Objetivo

Calcular hash SHA-256 de um arquivo e impedir a importação de arquivos
já presentes no acervo.

Status

Concluída

---

## Issue 20

Importação de PDFs

Status

Concluída

---

## Issue 21

Importação de Markdown

Status

Concluída

---

## Issue 22

Importação de Links

Status

Concluída

---

## Issue 22b

Importação de Docx

Objetivo

Extrair texto de documentos .docx (via python-docx) e importá-los para
o Acervo, seguindo exatamente o mesmo fluxo já usado por
importar_pdf/importar_markdown (hash, detecção de duplicata,
indexação automática, cópia física pelo ID em acervo/documentos/).

Usa o tipo "Documento" (não "Docx"), pensado para acomodar outros
formatos de documento de texto no futuro sem multiplicar tipos por
extensão.

Status

Concluída (não fazia parte do escopo original da Fase 6, mas foi
adicionada por ter complexidade baixa e reaproveitar 100% do padrão já
testado de importar_pdf -- ver docs/arquitetura.md, "a mídia é apenas
uma característica do objeto")

---

# EPIC 7 — Interface

## Issue 23

Dashboard

Status

Adiada para versão posterior ao MVP v1.0.0.

---

## Issue 24

Biblioteca

Status

Concluída

Observação: não virou uma tela/janela nova -- reaproveita literalmente
o mesmo componente de lista da área de Resultados (ResultadoItem),
conforme "Utiliza os mesmos componentes da pesquisa"
(docs/interface-grafica.md). `PesquisaController.listar_todos()` lista
os objetos ativos (via AcervoService), mais recente primeiro, sem
score (não há termo de busca para medir relevância). Acionada por um
botão "Biblioteca" na Barra Superior; a pesquisa continua funcionando
normalmente depois, sem que a Biblioteca deixe nenhum estado residual.

---

## Issue 25

Pesquisa

Status

Concluída (SearchBar na Barra Superior, PesquisaView renderiza os
resultados via PesquisaController)

---

## Issue 26

Editor Markdown

Status

Concluída

Observação: implementado como janela modal (`EditorMarkdownWindow`,
`ctk.CTkToplevel`), seguindo o mesmo padrão já usado pela Lixeira, em
vez de um frame embutido na janela principal. Acionado ao criar uma
Nota em branco pelo menu "Novo Objeto", e visível apenas para tipos
editáveis (`Nota`/`Markdown`). Ao salvar, o painel de Objeto em Foco é
atualizado automaticamente; ao fechar com alterações não salvas, pede
confirmação antes de descartar. Sem realce de sintaxe ou
pré-visualização, conforme decidido ("não pretende substituir editores
especializados").

---

## Issue 27

Configurações

Status

Concluída

Observação: o escopo não estava definido em nenhum documento (só
havia "Centraliza as configurações do sistema" e um config.json vazio
nunca lido por ninguém). Decisão tomada aqui: começar com apenas duas
preferências, as únicas coisas hoje hardcoded no código que fazem
sentido como preferência pessoal sem mexer em nada estrutural --
tema da interface (Sistema/Claro/Escuro, aplicado imediatamente via
`ctk.set_appearance_mode`) e quantidade de resultados semânticos por
busca (`PesquisaController`, antes fixo em 10). Implementado como
`ConfigService` (lê/escreve `config.json` com escrita atômica e
defaults seguros -- nunca falha por causa de um arquivo ausente,
corrompido ou desatualizado) + `ConfiguracoesWindow`, janela modal no
mesmo padrão de Lixeira/Backup/Editor Markdown.

---

# EPIC 8 — Backup

## Issue 28

Backup

Status

Concluída

Observação: implementado como `BackupService.criar_backup()`, gerando
um único arquivo .zip autocontido (`backups/wds_backup_AAAAMMDD_HHMMSS.zip`)
com banco.db + acervo/ + vetores/ juntos -- nunca uma cópia solta dos
três, para não permitir um backup parcial por engano
(docs/arquitetura.md, seção "Backup"). O banco.db é copiado via
`sqlite3.Connection.backup()`, não por cópia de arquivo bruta, para
garantir uma cópia consistente mesmo que outra conexão esteja
escrevendo no momento.

Correção associada: o caminho padrão do índice ChromaDB no código era
`chroma_db/`, divergente do `vetores/` já documentado em
docs/arquitetura.md. Corrigido em `embedding_service.py` para usar
`vetores/`, conforme AGENTS.md ("em caso de conflito, a arquitetura
sempre prevalece"). Ver também a nota de auditoria na Issue 32 sobre
a pasta `chroma_db/` residual encontrada versionada no Git.

---

## Issue 29

Restauração

Status

Concluída

Observação: `BackupService.restaurar_backup()` recusa backups
incompletos antes de tocar em qualquer arquivo (via
`validar_integridade()`), guarda uma cópia de segurança do estado
atual antes de sobrescrever, e reverte automaticamente para essa cópia
se qualquer etapa da extração falhar no meio do processo. Acessível
pela tela "Backup" (botão na Barra Superior), que lista os backups
existentes com opção de restaurar cada um. Exige reiniciar o WDS após
restaurar, já que objetos em memória (conexão do ChromaDB, cache dos
Services) não são recarregados automaticamente.

---

# EPIC 9 — Testes

## Issue 30

Testes Unitários

Status

Concluída na validação da release v1.0.0.

---

## Issue 31

Testes de Integração

Status

Concluída na validação da release v1.0.0, incluindo
`tests/test_integracao_acervo.py`.

---

# EPIC 10 — Release

## Issue 32

Versão 1.0

Status

Concluída. Taggeada como `v1.0.0` e publicada no repositório privado
`wds-repositorio-conhecimento`.

Decisão de empacotamento: a geração de um instalador formal via
PyInstaller foi tentada e abandonada -- bibliotecas pesadas do
projeto (`chromadb`, `sentence-transformers`) têm incompatibilidades
conhecidas e recorrentes com esse tipo de empacotador. No lugar,
adotou-se um lançador leve (`Abrir WDS.bat`, usando `pyw` para rodar
sem terminal visível) com atalho manual na Área de Trabalho. Critério
de "ícone clicável, sem terminal" atendido sem a complexidade de um
instalador.

Auditoria pré-release (encontrada e corrigida antes da tag v1.0.0):

1. `Toolbar` já exigia `ao_clicar_backup`, `ao_clicar_biblioteca` e
   `ao_clicar_configuracoes`, mas `MainWindow` ainda só conhecia
   Pesquisa, Novo Objeto e Lixeira -- os Services e Controllers de
   Backup e Configurações existiam mas nunca eram instanciados nem
   conectados. Corrigido: `MainWindow` agora monta `BackupService`,
   `ConfigService` e os respectivos Controllers, e conecta os três
   botões da Toolbar às janelas correspondentes.
2. `ObjetoController` não possuía um método `excluir()`, embora
   `ObjetoView` já chamasse `self._objeto_controller.excluir(objeto_id)`
   a partir do botão "Mover para Lixeira". Corrigido: `excluir()`
   adicionado, delegando a `AcervoService.excluir()` (já testado).
3. Existiam dois arquivos de view do mesmo painel (`objeto.py`,
   desatualizado e sem o botão de exclusão, e `objeto_view.py`, a
   versão correta) -- resíduo de um conflito de versionamento local.
   `main_window.py` foi confirmado apontando para `objeto_view.py`;
   `objeto.py` deve ser removido do projeto por estar obsoleto.
4. Repositório Git estava rastreando `chroma_db/` (pasta já presente
   no `.gitignore`, mas rastreada antes dessa regra existir) e não
   protegia `vetores/` nem `backups/` -- ambos contêm dados pessoais
   do acervo (embeddings e cópias completas, respectivamente).
   Corrigido: `.gitignore` atualizado, pastas destrancadas do
   rastreamento via `git rm --cached`, estrutura preservada com
   `.gitkeep` no mesmo padrão já usado em `acervo/`.

Nenhum dos quatro pontos exigiu mudança de arquitetura -- todos eram
integração faltante ou higiene de repositório, não lógica de negócio
nova.
