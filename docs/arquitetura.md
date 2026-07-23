# Arquitetura — WDS Acervo de Conhecimento

**Versão 4**

Este documento define a arquitetura do WDS (Willian Dias Santos) – Acervo de Conhecimento, uma aplicação desktop em Python destinada à preservação, organização, relacionamento e recuperação de conhecimento pessoal.

O documento estabelece as decisões arquiteturais do projeto e serve como referência para toda implementação.

---

# Objetivo

O WDS permite que o usuário construa um **Acervo de Conhecimento**, reunindo diferentes tipos de informação em um único ambiente.

Cada item armazenado é tratado como um **Objeto de Conhecimento**, independentemente de sua mídia.

O sistema organiza conhecimento por meio de metadados, relacionamentos e mecanismos de busca, preservando a independência entre o modelo de domínio e o formato físico dos arquivos.

---

# Princípios Arquiteturais

- Dados locais (offline).
- Código modular.
- Arquitetura em camadas.
- Separação entre domínio e interface.
- Baixo acoplamento.
- Alta coesão.
- Fácil expansão.
- Interface responsiva.
- Busca eficiente.
- Arquivos acessíveis fora da aplicação.
- Nenhum componente é incorporado sem possibilidade de testes objetivos.

---

# Modelo de Domínio

O elemento central do sistema é o **Objeto de Conhecimento**.

Um Objeto de Conhecimento representa qualquer informação considerada relevante pelo usuário, independentemente do formato em que esteja armazenada.

Exemplos:

- notas
- pensamentos
- documentos
- PDFs
- livros
- artigos
- imagens
- fotografias
- áudios
- vídeos
- links
- pessoas
- conceitos
- projetos
- citações

Todos compartilham o mesmo modelo de domínio.

A mídia é apenas uma característica do objeto, nunca sua definição arquitetural.

---

# Tecnologias

| Camada | Tecnologia |
|---------|------------|
| Linguagem | Python 3 |
| Interface | CustomTkinter |
| Persistência | SQLite |
| Busca textual | SQLite FTS5 |
| Busca semântica | ChromaDB |
| Embeddings | sentence-transformers (modelo multilíngue) |
| PDF | PyMuPDF |
| Texto | Markdown |
| Configuração | JSON |
| Processamento assíncrono | threading |

---

# Organização dos Arquivos

A organização lógica do acervo é realizada pelo banco de dados.

A estrutura física dos diretórios existe apenas para armazenamento.

Os arquivos nunca são organizados por assunto ou categoria.

O nome físico utiliza sempre o identificador do objeto.

```
Projeto/

├── app.py
├── banco.db
├── config.json
│
├── acervo/
│   ├── documentos/
│   ├── imagens/
│   ├── audios/
│   ├── videos/
│   └── outros/
│
├── vetores/
│
└── backups/
```

Caso novos tipos de mídia sejam suportados futuramente, a arquitetura permanece inalterada.

---

# Arquitetura em Camadas

## Interface

Responsável exclusivamente pela interação com o usuário.

Exemplos:

- Dashboard
- Pesquisa
- Biblioteca
- Visualização dos Objetos
- Configurações

A interface nunca implementa regras de negócio.

---

## Serviços

Contém toda a lógica da aplicação.

Responsabilidades:

- cadastro de objetos;
- edição;
- exclusão;
- importação;
- pesquisa;
- indexação;
- gerenciamento de tags;
- gerenciamento de relacionamentos;
- detecção de duplicatas;
- lixeira.

Toda regra de negócio pertence a esta camada.

---

## Persistência

Responsável pelo armazenamento dos dados.

### SQLite

Armazena:

- objetos;
- metadados;
- tags;
- relacionamentos;
- configurações;
- histórico.

É a fonte oficial dos dados do sistema.

### ChromaDB

Armazena exclusivamente os vetores utilizados na busca semântica.

Utiliza o mesmo identificador do objeto existente no SQLite.

Nunca duplica metadados.

### Sistema de Arquivos

Armazena apenas os arquivos físicos pertencentes ao acervo.

---

# Processamento em Segundo Plano

Operações potencialmente demoradas executam em threads independentes.

Exemplos:

- importação;
- extração de texto;
- geração de embeddings;
- indexação.

A interface permanece responsiva durante todo o processamento.

**Decisão de sequenciamento**: a implementação efetiva de threading para
essas operações fica adiada para a Fase 7 (Interface Gráfica). Até o
momento, `ImportacaoService` e `AcervoService` executam essas operações
de forma síncrona, pois não existe interface gráfica que possa travar —
não há benefício em introduzir concorrência antes de haver uma tela para
proteger. Esta seção descreve o comportamento esperado do produto
finalizado, não o estado atual da Fase 6.

---

# Busca

O sistema possui dois mecanismos independentes.

## Busca Textual

Baseada no SQLite FTS5.

Utilizada para localizar palavras e expressões exatas.

---

## Busca Semântica

Baseada em embeddings armazenados no ChromaDB.

Permite localizar Objetos de Conhecimento semelhantes em significado.

Sua permanência depende da demonstração de benefício prático durante o uso do sistema.

---

# Modelo Inicial de Dados

## Objetos

Cada Objeto de Conhecimento possui, inicialmente:

- id
- título
- tipo
- caminho
- resumo
- hash
- status
- data de criação
- data de edição
- data de exclusão

---

## Tags

Permitem organização lógica independente da estrutura física.

---

## Relacionamentos

Conectam Objetos de Conhecimento entre si.

Os relacionamentos independem do tipo de mídia.

Auto-relações não são permitidas: a origem e o destino de um relacionamento
devem sempre ser Objetos de Conhecimento distintos.

Quando um objeto é excluído logicamente e movido para a lixeira, suas relações
permanecem inalteradas. Isso preserva os vínculos para que sejam recuperados
quando o objeto for restaurado.

Na exclusão definitiva de um objeto da lixeira, as associações de tags e todas
as relações em que ele é origem ou destino são removidas na mesma transação.
As Tags e os demais Objetos de Conhecimento envolvidos permanecem preservados.

---

## Vetores

Os embeddings permanecem exclusivamente no ChromaDB.

Cada vetor utiliza o mesmo identificador do objeto correspondente no SQLite.

---

## Detecção de Duplicatas

A verificação de duplicidade por hash de arquivo considera apenas Objetos
de Conhecimento com status ativo.

Um arquivo cujo hash já esteja associado a um objeto na lixeira pode ser
reimportado normalmente. A permanência de um objeto na lixeira é entendida
como sinal de que o usuário não deseja mais aquele conteúdo ativo no
acervo, portanto reimportar o mesmo arquivo não constitui uma duplicata
indevida.

Links (tipo `Link`) não possuem arquivo físico nem hash de conteúdo. Sua
detecção de duplicata é feita comparando diretamente a URL armazenada em
`caminho` entre os objetos ativos, seguindo a mesma regra: um link na
lixeira não bloqueia o recadastro da mesma URL.

O cadastro de links não busca automaticamente título ou descrição da
página de destino — isso exigiria uma requisição web a partir da
aplicação, fora do escopo atual. Título e resumo, quando não informados
explicitamente, usam a própria URL como valor padrão de título.

---

# Fluxo Geral

1. Importação ou criação de um Objeto de Conhecimento.
2. Armazenamento dos metadados.
3. Armazenamento do arquivo físico, quando existir.
4. Indexação textual.
5. Geração do embedding (quando aplicável).
6. Organização por metadados.
7. Recuperação por pesquisa ou navegação.

---

# Backup

Um backup completo deve conter:

- banco.db
- pasta acervo/
- pasta vetores/

A ausência de qualquer um desses componentes torna o backup incompleto.

---

# Evolução da Arquitetura

A arquitetura foi projetada para evolução incremental.

Novas funcionalidades devem reutilizar o modelo de Objeto de Conhecimento existente.

Mudanças arquiteturais somente podem ocorrer mediante atualização desta documentação.

---

# Fora do Escopo da Arquitetura Atual

As funcionalidades abaixo permanecem planejadas para versões futuras e não fazem parte desta arquitetura:

- IA generativa local;
- perguntas em linguagem natural;
- extração automática de conceitos;
- extração automática de relacionamentos;
- grafo de conhecimento;
- integração com outros agentes.

Esses recursos somente poderão ser incorporados após validação técnica e atualização desta arquitetura.
