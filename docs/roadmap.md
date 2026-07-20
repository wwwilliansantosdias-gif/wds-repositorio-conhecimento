# Roadmap de Desenvolvimento

## Objetivo

Este documento define a sequência oficial de desenvolvimento do WDS – Acervo de Conhecimento.

Cada fase representa um incremento funcional completo, devendo ser implementada, testada e validada antes do início da fase seguinte.

Nenhuma funcionalidade deve ser antecipada sem atualização deste Roadmap.

---

# Princípios

Todo desenvolvimento deve respeitar:

- o Conceito do Acervo de Conhecimento;
- a Arquitetura do projeto;
- o AGENTS.md;
- este Roadmap.

A implementação é incremental.

Cada fase deve entregar software funcional.

---

# Fase 1 — Fundação

## Objetivo

Estabelecer a estrutura inicial do projeto.

## Itens

- Estrutura de diretórios
- Ambiente Python
- pyproject.toml
- requirements.txt
- .gitignore
- Configuração inicial
- app.py
- Organização dos módulos

## Critério de conclusão

O projeto executa corretamente e possui a estrutura básica definida.

---

# Fase 2 — Persistência

## Objetivo

Implementar a infraestrutura de armazenamento dos metadados.

## Itens

- SQLite
- Inicialização automática
- Criação das tabelas
- Camada de persistência
- Migração inicial

## Critério de conclusão

O banco é criado automaticamente e todas as tabelas estão disponíveis.

---

# Fase 3 — Modelo de Domínio

## Objetivo

Implementar o modelo de Objetos de Conhecimento.

## Itens

- Objeto de Conhecimento
- Tag
- Relacionamento

## Critério de conclusão

Todos os modelos estão implementados e possuem testes automatizados.

---

# Fase 4 — Serviços

## Objetivo

Implementar toda a lógica de negócio da aplicação.

## Itens

- Cadastro
- Atualização
- Exclusão
- Lixeira
- Tags
- Relacionamentos
- Validações
- Regras de negócio

## Critério de conclusão

Todos os serviços funcionam corretamente e possuem testes.

---

# Fase 5 — Pesquisa

## Objetivo

Implementar os mecanismos de recuperação da informação.

## Itens

### Busca textual

- SQLite FTS5

### Busca semântica

- ChromaDB
- sentence-transformers

## Critério de conclusão

As pesquisas textual e semântica retornam resultados consistentes.

---

# Fase 6 — Importação

## Objetivo

Permitir a incorporação de conteúdo ao Acervo de Conhecimento.

## Itens

- Importação de PDFs
- Importação de Markdown
- Cadastro de links
- Extração de texto
- Detecção de duplicatas
- Indexação em segundo plano

## Critério de conclusão

Os conteúdos são importados, armazenados e indexados corretamente.

---

# Fase 7 — Interface Gráfica

## Objetivo

Disponibilizar uma interface completa para utilização do sistema.

## Itens

- Dashboard
- Biblioteca
- Pesquisa
- Visualização dos Objetos
- Editor Markdown
- Configurações

## Critério de conclusão

Todas as funcionalidades do MVP podem ser utilizadas pela interface.

---

# Fase 8 — Backup e Recuperação

## Objetivo

Garantir a preservação do Acervo de Conhecimento.

## Itens

- Backup
- Restauração
- Validação de integridade

## Critério de conclusão

O sistema restaura integralmente um backup válido.

---

# Fase 9 — Testes e Validação

## Objetivo

Garantir a qualidade do sistema antes da primeira versão.

## Itens

- Testes unitários
- Testes de integração
- Testes da persistência
- Testes dos serviços
- Testes da pesquisa

## Critério de conclusão

Todos os testes são aprovados.

---

# Fase 10 — Release 1.0

## Objetivo

Preparar a primeira versão pública do sistema.

## Itens

- Revisão da documentação
- Ajustes finais
- Empacotamento
- Geração do instalador

## Critério de conclusão

Versão 1.0 pronta para distribuição.

---

# Evolução Pós-MVP

As funcionalidades abaixo permanecem fora do escopo da versão 1.0 e somente poderão ser implementadas mediante atualização da arquitetura e deste Roadmap.

- OCR
- Transcrição de áudio
- Inteligência Artificial generativa
- Perguntas em linguagem natural
- Extração automática de conceitos
- Extração automática de relacionamentos
- Grafo de conhecimento
- Integração com agentes externos

Essas funcionalidades deverão reutilizar o modelo de Objeto de Conhecimento existente, preservando a arquitetura do sistema.
