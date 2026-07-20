# WDS – Acervo de Conhecimento

O WDS (Web Document System) é uma aplicação desktop desenvolvida em Python para preservação, organização, relacionamento e recuperação de conhecimento pessoal.

Seu objetivo é permitir que cada usuário construa um **Acervo de Conhecimento** ao longo da vida, reunindo diferentes tipos de conteúdo em um único ambiente, independentemente do formato da informação.

---

# Objetivo

O WDS organiza conhecimento, não apenas arquivos.

Cada conteúdo armazenado é tratado como um **Objeto de Conhecimento**, podendo representar documentos, imagens, áudios, vídeos, anotações, códigos, fotografias ou qualquer outra mídia que possua significado para o usuário.

O sistema fornece mecanismos para:

- preservar conhecimento;
- organizar objetos;
- relacionar informações;
- recuperar conteúdo rapidamente;
- permitir evolução contínua do acervo.

O significado de cada objeto é definido exclusivamente pelo usuário.

---

# Princípios

- O conhecimento é independente da mídia.
- O usuário define o que possui valor para seu acervo.
- O armazenamento físico é separado da organização lógica.
- Objetos podem evoluir continuamente por meio do enriquecimento de metadados.
- O sistema pode sugerir relações futuramente, mas nunca substituir as decisões do usuário.

---

# MVP

A primeira versão do WDS possui foco em:

- armazenamento em SQLite;
- gerenciamento de Objetos de Conhecimento;
- organização por metadados;
- gerenciamento de tags;
- relacionamentos entre objetos;
- pesquisa utilizando metadados.

Recursos como OCR, transcrição, busca semântica, IA e indexação vetorial fazem parte da evolução futura do projeto.

---

# Tecnologias

- Python
- CustomTkinter
- SQLite
- Arquitetura em camadas
- Testes automatizados com unittest

Tecnologias planejadas para versões futuras:

- SQLite FTS5
- ChromaDB
- Inteligência Artificial

---

# Estrutura do Projeto

```
docs/
src/
tests/

app.py
README.md
AGENTS.md
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