# AGENTS.md

## Objetivo

Este repositório contém a implementação do projeto
"WDS Repositório de Conhecimento".

Todo desenvolvimento deve respeitar a arquitetura definida em:

docs/arquitetura.md

Se houver conflito entre uma implementação e a arquitetura,
a arquitetura prevalece.

---

# Papel do agente

O agente atua como desenvolvedor Python sênior.

Antes de modificar qualquer arquivo:

1. Ler docs/arquitetura.md.
2. Verificar se a alteração está de acordo com a arquitetura.
3. Caso exista conflito, interromper a implementação e informar o motivo.

Nunca assumir requisitos que não estejam documentados.

---

# Escopo

Implementar somente o que for solicitado na Issue atual.

Não antecipar funcionalidades futuras.

Não adicionar dependências sem necessidade.

---

# Linguagem

Python 3.14

---

# Interface

CustomTkinter

---

# Banco

SQLite

---

# Busca textual

SQLite FTS5

---

# Busca por significado

ChromaDB

sentence-transformers

Modelo multilíngue.

---

# Organização

Todo código deve permanecer modular.

Separar:

- interface
- serviços
- persistência
- modelos
- utilitários

---

# Banco de dados

O SQLite é a fonte principal de metadados.

O ChromaDB armazena apenas vetores.

Nunca duplicar informações entre eles.

---

# Arquivos

Os arquivos do usuário ficam em:

acervo/

Nunca utilizar o título do objeto como nome do arquivo.

O identificador é sempre o id do banco.

---

# Threads

Toda importação pesada deve executar em segundo plano.

A interface nunca deve bloquear.

---

# Código

Priorizar:

- simplicidade
- legibilidade
- baixo acoplamento
- alta coesão

Evitar:

- código duplicado
- funções muito grandes
- classes gigantes
- dependências desnecessárias

---

# Testes

Toda funcionalidade nova deve possuir testes.

Nenhuma implementação é considerada concluída se não puder ser testada.

---

# Restrições

Não alterar a arquitetura.

Não substituir bibliotecas sem justificativa.

Não criar funcionalidades fora da Issue.

Não alterar comportamento existente sem necessidade.

---

# Fluxo

Sempre seguir:

Issue

↓

Implementação

↓

Testes

↓

Pull Request

↓

Revisão

↓

Merge

Nunca pular etapas.

---

# Em caso de dúvida

Perguntar antes de implementar.

Não inventar requisitos.

Não criar funcionalidades por iniciativa própria.
