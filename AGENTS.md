# AGENTS.md

# Objetivo

Este repositório contém a implementação do projeto **WDS – Acervo de Conhecimento**.

O WDS é uma aplicação desktop em Python destinada à preservação, organização, relacionamento e recuperação de conhecimento pessoal.

Todo desenvolvimento deve respeitar rigorosamente a arquitetura definida em:

```
docs/arquitetura.md
```

Em caso de conflito entre qualquer implementação e a documentação arquitetural, a arquitetura sempre prevalece.

---

# Papel do Agente

O agente atua como desenvolvedor Python sênior responsável por implementar funcionalidades de forma incremental e consistente.

Antes de modificar qualquer arquivo, deve obrigatoriamente:

1. Ler `docs/arquitetura.md`.
2. Verificar se a alteração está de acordo com a arquitetura.
3. Confirmar que a implementação pertence à fase atual do Roadmap.
4. Caso exista conflito, interromper a implementação e informar o motivo.

Nunca assumir requisitos que não estejam documentados.

Nunca criar funcionalidades por iniciativa própria.

---

# Princípios do Projeto

O modelo de domínio do WDS é baseado no conceito de **Objeto de Conhecimento**.

Todo conteúdo armazenado representa um Objeto de Conhecimento, independentemente de sua mídia.

Documentos, imagens, áudios, vídeos, fotografias, códigos, anotações ou qualquer outro formato utilizam o mesmo modelo conceitual.

Novos tipos de mídia nunca devem alterar o modelo de domínio.

---

# Escopo

Implementar exclusivamente o que for solicitado pela Issue ou incremento atual.

Não antecipar funcionalidades futuras.

Não adicionar dependências sem necessidade.

Não alterar requisitos arquiteturais.

---

# Linguagem

Python 3.14

---

# Interface

CustomTkinter

---

# Persistência

SQLite é a fonte oficial de todos os metadados.

---

# Busca Textual

SQLite FTS5

---

# Busca Semântica

ChromaDB

sentence-transformers

Modelo multilíngue.

O banco vetorial é complementar ao SQLite.

Nunca duplicar informações entre ambos.

---

# Organização do Código

O projeto deve permanecer organizado em camadas.

Separar responsabilidades entre:

- interface
- serviços
- persistência
- modelos
- utilitários

Toda regra de negócio deve permanecer na camada de serviços.

Evitar dependências cruzadas entre camadas.

---

# Arquivos do Usuário

Os arquivos pertencentes ao Acervo de Conhecimento ficam armazenados em:

```
acervo/
```

O nome físico do arquivo nunca deve utilizar o título do objeto.

O identificador oficial é sempre o ID registrado no banco de dados.

---

# Desempenho

Operações demoradas devem executar em segundo plano.

A interface gráfica nunca deve bloquear durante importações, indexações ou processamentos.

---

# Qualidade do Código

Priorizar sempre:

- simplicidade
- legibilidade
- baixo acoplamento
- alta coesão
- reutilização
- manutenção

Evitar:

- código duplicado
- funções excessivamente grandes
- classes monolíticas
- dependências desnecessárias
- otimizações prematuras

---

# Testes

Toda funcionalidade nova deve possuir testes automatizados.

Nenhuma implementação é considerada concluída sem validação por testes.

Sempre que possível:

- testar regras de negócio;
- testar serviços;
- testar persistência;
- evitar dependência da interface gráfica.

---

# Restrições

Não alterar a arquitetura.

Não modificar o modelo de domínio sem atualização da documentação.

Não substituir bibliotecas sem justificativa.

Não criar funcionalidades fora da Issue atual.

Não alterar comportamento existente sem necessidade.

Não introduzir acoplamentos desnecessários.

---

# Fluxo de Desenvolvimento

Todo desenvolvimento deve seguir obrigatoriamente o fluxo:

```
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
```

Nenhuma etapa deve ser ignorada.

---

# Em Caso de Dúvida

Quando houver ambiguidade ou ausência de requisitos:

- interromper a implementação;
- solicitar esclarecimentos;
- nunca inventar requisitos;
- nunca assumir comportamentos não documentados.

A documentação do projeto sempre possui prioridade sobre interpretações da implementação existente.