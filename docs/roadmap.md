# Roadmap de Desenvolvimento

## Objetivo

Este documento define a ordem oficial de desenvolvimento do projeto.

Cada fase deve ser concluída, testada e revisada antes do início da próxima.

Nenhuma funcionalidade deve ser implementada fora da fase correspondente.

---

# Fase 1 — Fundação

Objetivo:

Criar a estrutura básica do projeto.

Itens:

- Estrutura de pastas
- Ambiente Python
- pyproject.toml
- requirements.txt
- .gitignore
- Configuração inicial
- app.py
- Organização dos módulos

Critério de conclusão:

O projeto executa sem erros.

---

# Fase 2 — Banco de Dados

Objetivo:

Criar toda a persistência de dados.

Itens:

- SQLite
- Criação automática do banco
- Criação das tabelas
- Camada de acesso aos dados
- Migração inicial

Critério de conclusão:

O banco é criado automaticamente.

---

# Fase 3 — Modelos

Objetivo:

Criar os modelos da aplicação.

Itens:

- Objeto
- Tag
- Relação

Critério de conclusão:

Todos os modelos possuem testes.

---

# Fase 4 — Serviços

Objetivo:

Implementar a lógica de negócio.

Itens:

- Cadastro
- Atualização
- Exclusão
- Lixeira
- Tags
- Relacionamentos

Critério de conclusão:

CRUD completo funcionando.

---

# Fase 5 — Pesquisa

Objetivo:

Implementar os mecanismos de busca.

Itens:

- SQLite FTS5
- Pesquisa textual
- ChromaDB
- Pesquisa por significado

Critério de conclusão:

As duas pesquisas funcionam.

---

# Fase 6 — Importação

Objetivo:

Importar conteúdo externo.

Itens:

- PDFs
- Links
- Markdown

Critério de conclusão:

Importação completa.

---

# Fase 7 — Interface

Objetivo:

Criar a interface gráfica.

Itens:

- Dashboard
- Biblioteca
- Pesquisa
- Editor
- Configurações

Critério de conclusão:

Aplicação utilizável.

---

# Fase 8 — Backup

Objetivo:

Garantir recuperação dos dados.

Itens:

- Backup
- Restauração
- Validação

Critério de conclusão:

Backup testado.

---

# Fase 9 — Testes

Objetivo:

Validar todo o sistema.

Itens:

- Testes unitários
- Testes de integração
- Testes de persistência

Critério de conclusão:

Todos os testes aprovados.

---

# Fase 10 — Release

Objetivo:

Preparar a primeira versão.

Itens:

- Documentação
- Ajustes finais
- Empacotamento

Critério de conclusão:

Versão 1.0 pronta para uso.
