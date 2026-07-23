# WDS – Acervo de Conhecimento

O WDS (Willian Dias Santos) – Acervo de Conhecimento é uma aplicação desktop desenvolvida em Python para preservação, organização, relacionamento e recuperação de conhecimento pessoal.

Seu objetivo é permitir que cada usuário construa um **Acervo de Conhecimento** ao longo da vida, reunindo diferentes tipos de conteúdo em um único ambiente, independentemente do formato da informação.

---

# Objetivo

O WDS organiza conhecimento, não apenas arquivos.

Cada conteúdo armazenado é tratado como um **Objeto de Conhecimento**, podendo representar documentos, imagens, áudios, vídeos, anotações, códigos, fotografias ou qualquer outra mídia que possua significado para o usuário.

O sistema fornece mecanismos para:

- preservar conhecimento;
- organizar objetos;
- relacionar informações;
- recuperar conteúdo rapidamente, por palavra-chave ou por significado;
- permitir evolução contínua do acervo.

O significado de cada objeto é definido exclusivamente pelo usuário.

---

# Princípios

- O conhecimento é independente da mídia.
- O usuário define o que possui valor para seu acervo.
- O armazenamento físico é separado da organização lógica.
- Objetos podem evoluir continuamente por meio do enriquecimento de metadados.
- O sistema pode sugerir relações automaticamente (por similaridade semântica), mas nunca substitui as decisões do usuário.

---

# Estado Atual do Projeto

- Persistência em SQLite (com integridade referencial via chaves estrangeiras)
- Gerenciamento completo de Objetos de Conhecimento (cadastro, atualização, exclusão lógica e definitiva, lixeira)
- Gerenciamento de Tags e Relacionamentos entre objetos
- Pesquisa textual (SQLite FTS5), com suporte a acentuação e prefixo
- Pesquisa semântica (ChromaDB + sentence-transformers), com sincronização automática ao cadastrar, atualizar ou excluir objetos
- Detecção de duplicatas por hash de arquivo (fundação da Fase de Importação)

Em desenvolvimento:

- Importação de PDFs, Markdown e links, com extração automática de texto
- Interface gráfica (CustomTkinter)
- Backup e recuperação

Consulte `docs/roadmap.md` e `docs/docs/issues.md` para o detalhamento completo de cada fase e o progresso atualizado.

---

# Tecnologias

- Python
- CustomTkinter
- SQLite (com FTS5)
- ChromaDB
- sentence-transformers (modelo multilíngue)
- Arquitetura em camadas
- Testes automatizados com unittest

---

# Estrutura do Projeto

```
docs/
src/
tests/
acervo/
backups/
vetores/

app.py
README.md
AGENTS.md
pyproject.toml
```

---

# Documentação

Toda a documentação arquitetural está disponível na pasta `docs`.

O projeto é desenvolvido de forma incremental, seguindo rigorosamente:

- Arquitetura
- Roadmap
- AGENTS.md
- Decisões arquiteturais

---

# Estado do Projeto

O desenvolvimento ocorre por fases previamente definidas.

Cada fase possui escopo próprio e somente é implementada após validação da fase anterior.

Essa abordagem garante estabilidade da arquitetura e reduz retrabalho durante a evolução do sistema.

---

# Licença

Projeto em desenvolvimento.
