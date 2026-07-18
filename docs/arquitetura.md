# Projeto — Repositório Pessoal de Conhecimento (Protótipo em Python)

**Versão 3** — fundação da v2 (validada) + uma única adição: busca por significado. As apostas do segundo documento (IA generativa local, extração automática de conceitos, grafo, integração multi-agente) ficam fora por enquanto — ver seção final, com o motivo de cada uma.

## Objetivo

Aplicação desktop em Python para armazenar, organizar e recuperar
conhecimento pessoal — pensamentos, PDFs, links, livros, conceitos —
com busca tanto por palavra exata quanto por significado.

------------------------------------------------------------------------

# Princípios

-   Dados locais (offline).
-   Código modular.
-   Fácil expansão.
-   Interface simples.
-   Busca rápida.
-   Arquivos legíveis fora da aplicação.
-   Nenhuma peça entra na arquitetura sem ser testável de forma objetiva.

------------------------------------------------------------------------

# Tecnologias

  Camada              Tecnologia
  ------------------- -------------------------
  Linguagem           Python 3
  Interface            CustomTkinter
  Banco de dados       SQLite
  Busca por palavra    SQLite FTS5
  Busca por sentido    ChromaDB + sentence-transformers (modelo multilíngue) 🆕
  PDFs                 PyMuPDF
  Texto                Markdown
  Configurações        JSON
  Segundo plano        threading (módulo padrão do Python)

------------------------------------------------------------------------

# Estrutura de Pastas

A pasta não organiza — quem organiza é o banco (tags e relações). Todo
arquivo é salvo internamente pelo seu `id`, não pelo título.

``` text
Repositorio/

├── app.py
├── banco.db
├── config.json
│
├── acervo/
│   ├── pdfs/
│   ├── notas/
│   ├── imagens/
│   └── links/
│
├── vetores/          (base do ChromaDB) 🆕
│
└── backups/
```

------------------------------------------------------------------------

# Arquitetura

## Camada de Interface

-   Dashboard
-   Pesquisa (palavra + sentido) 🆕
-   Biblioteca
-   Editor Markdown
-   Configurações

## Camada de Serviços

-   Cadastro
-   Pesquisa
-   Importação de PDF
-   Indexação (texto e vetor) 🆕
-   Tags
-   Relacionamentos
-   Detecção de duplicatas
-   Lixeira / exclusão reversível

## Camada de Persistência

-   SQLite — metadados (título, caminho, tipo, tags, relações, status).
-   ChromaDB — vetor de significado de cada objeto, referenciado pelo mesmo `id` do SQLite. 🆕
-   Arquivos Markdown/PDF — conteúdo original.

## Processamento em Segundo Plano

Toda importação/indexação (incluindo geração do vetor de significado)
roda numa thread separada, desde a v1. Evita travar a interface.

------------------------------------------------------------------------

# Busca por Significado 🆕

Ao salvar um objeto, o texto é transformado num vetor numérico que
representa seu sentido (não suas palavras exatas), via
sentence-transformers. Esse vetor é guardado no ChromaDB.

Na pesquisa, o usuário pode escolher:
-   **Busca por palavra** (FTS5) — encontra o termo exato.
-   **Busca por sentido** (ChromaDB) — encontra o que é parecido em
    significado, mesmo com palavras diferentes.

Critério de sucesso: a busca por sentido só permanece na v1 se, no uso
real, devolver resultados úteis que a busca por palavra não encontraria.
Caso contrário, é descartada — não é adicionada complexidade permanente
sem retorno comprovado.

------------------------------------------------------------------------

# Tipos de Objetos

Pensamento, PDF, Livro, Artigo, Link, Pessoa, Conceito, Projeto,
Citação. Todos podem se relacionar entre si.

------------------------------------------------------------------------

# Funcionalidades da Primeira Versão

-   Cadastro de pensamentos
-   Editor Markdown
-   Cadastro de links
-   Cadastro de PDFs
-   Sistema de tags
-   Pesquisa textual (palavra)
-   Pesquisa por significado 🆕
-   Abertura do arquivo original
-   Organização por tags (não por pasta)
-   Detecção de duplicata na importação
-   Exclusão para lixeira
-   Importação/indexação em thread separada

------------------------------------------------------------------------

# Banco de Dados (Modelo Inicial)

## tabela_objetos

id, titulo, tipo, caminho, resumo, hash_arquivo, status (ativo/lixeira),
data_criacao, data_edicao, data_exclusao

## tabela_tags

id, nome

## tabela_objeto_tag

objeto_id, tag_id

## tabela_relacoes

origem, destino, tipo_relacao

## Vetores (ChromaDB, fora do SQLite) 🆕

Cada entrada usa o mesmo `id` de tabela_objetos como chave — não existe
tabela extra no SQLite para isso, o ChromaDB guarda seu próprio índice.

------------------------------------------------------------------------

# Backup

Um backup só é válido se copiar `banco.db` + pasta `acervo/` + pasta
`vetores/` juntos. 🆕 Faltando qualquer uma das três, o backup fica
inconsistente.

------------------------------------------------------------------------

# Fluxo de Uso

1.  Adicionar um PDF (checa duplicata antes de salvar).
2.  Extrai texto, gera vetor de significado, indexa por palavra. 🆕
3.  Criar nota em Markdown, associar tags, relacionar a outros objetos.
4.  Pesquisar por palavra exata **ou** por sentido.
5.  Abrir qualquer conteúdo diretamente.
6.  Excluir manda para a lixeira.

------------------------------------------------------------------------

# Fora de Escopo por Enquanto

Itens do segundo documento que **não** entram nesta versão — e o
motivo específico de cada um, para não serem reintroduzidos sem
critério mais tarde:

-   **IA generativa local (Ollama) / perguntas em linguagem natural** — depende de RAM/hardware da máquina, ainda não avaliado.
-   **Extração automática de conceitos e relações** — sem solução confiável para texto filosófico/aforístico; risco alto de gerar ruído em vez de conexões reais.
-   **Grafo de conhecimento** — só compensa quando o acervo tiver volume suficiente para existir rede de relações que valha visualizar.
-   **Integração com outros agentes (WDS, Comercial etc.)** — depende de cada uma dessas ferramentas já estar madura o bastante para expor uma interface de consulta.

Cada um desses pode voltar como uma fase futura independente, quando
tiver uma forma objetiva de testar se funciona — não antes. 
