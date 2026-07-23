# Backlog do Projeto

Este documento define todas as Issues planejadas para o desenvolvimento.

As Issues devem ser implementadas na ordem apresentada.

Nenhuma Issue deve alterar a arquitetura definida em
docs/arquitetura.md.

---

# Progresso Geral

**19 de 32 Issues concluidas (~59%).**

Esta contagem pesa cada Issue igualmente e nao reflete o esforco real de
cada uma -- a Fase 7 (Interface Grafica), por exemplo, tende a exigir
muito mais trabalho do que uma unica Issue de banco de dados. Use como
direcao aproximada, nao como medida precisa.

Atualizar esta secao e o campo Status de cada Issue sempre que uma fase
for concluida.

| Fase | Status |
|---|---|
| 1 -- Fundacao | Concluida |
| 2 -- Persistencia | Concluida |
| 3 -- Modelo de Dominio | Concluida |
| 4 -- Servicos | Concluida |
| 5 -- Pesquisa | Concluida |
| 6 -- Importacao | Em andamento (~15%) |
| 7 -- Interface Grafica | Nao iniciada |
| 8 -- Backup e Recuperacao | Nao iniciada |
| 9 -- Testes e Validacao | Nao iniciada |
| 10 -- Release 1.0 | Nao iniciada |

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

Concluida

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

Concluida

---

## Issue 3

Título

Inicialização da aplicação

Objetivo

Criar app.py.

Critérios

Aplicação abre sem erros.

Status

Concluida

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

Concluida

---

## Issue 5

Título

Criar tabela_objetos

Status

Concluida

---

## Issue 6

Título

Criar tabela_tags

Status

Concluida

---

## Issue 7

Título

Criar tabela_objeto_tag

Status

Concluida

---

## Issue 8

Título

Criar tabela_relacoes

Status

Concluida

---

# EPIC 3 — Modelos

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

Modelo Relação

Status

Concluida

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

Concluida

---

## Issue 17

Pesquisa textual

Status

Concluida

---

## Issue 18

Integração ChromaDB

Status

Concluida

---

## Issue 19

Busca por significado

Status

Concluida

Observação: inclui a sincronia automatica entre cadastro/atualizacao/
exclusao de objetos e o indice semantico, via AcervoService (nao
formalizado como Issue separada no backlog original).

---

# EPIC 6 — Importação

## Issue 19b

Detecção de duplicatas (fundação)

Objetivo

Calcular hash SHA-256 de um arquivo e impedir a importacao de arquivos
ja presentes no acervo.

Status

Concluida (base implementada em ImportacaoService; ainda nao integrada
ao fluxo completo de importacao)

---

## Issue 20

Importação de PDFs

Status

Não iniciada

---

## Issue 21

Importação de Markdown

Status

Não iniciada

---

## Issue 22

Importação de Links

Status

Não iniciada

---

# EPIC 7 — Interface

## Issue 23

Dashboard

Status

Não iniciada

---

## Issue 24

Biblioteca

Status

Não iniciada

---

## Issue 25

Pesquisa

Status

Não iniciada

---

## Issue 26

Editor Markdown

Status

Não iniciada

---

## Issue 27

Configurações

Status

Não iniciada

---

# EPIC 8 — Backup

## Issue 28

Backup

Status

Não iniciada

---

## Issue 29

Restauração

Status

Não iniciada

---

# EPIC 9 — Testes

## Issue 30

Testes Unitários

Status

Em andamento continuo (testes acompanham cada fase; validacao final
formal ainda nao realizada)

---

## Issue 31

Testes de Integração

Status

Em andamento continuo (existe tests/test_integracao_acervo.py cobrindo
Objeto+Tag+Relacao; cobertura completa ainda pendente)

---

# EPIC 10 — Release

## Issue 32

Versão 1.0

Status

Não iniciada
