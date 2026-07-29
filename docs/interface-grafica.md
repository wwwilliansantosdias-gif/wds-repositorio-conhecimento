# Interface Gráfica

## Objetivo

A Interface Gráfica é responsável por disponibilizar todas as funcionalidades do MVP do WDS por meio de uma experiência simples, limpa e funcional.

A interface não implementa regras de negócio.

Toda lógica permanece concentrada nos Services.

---

# Princípios

A interface deve seguir os princípios abaixo.

- Limpa.
- Simples.
- Funcional.
- Conteúdo acima da interface.
- Pesquisa é a principal forma de acesso ao conhecimento.
- Existe apenas um Objeto de Conhecimento em foco.
- O contexto permite explorar o conhecimento.
- O usuário nunca perde a pesquisa original.

---

# Estrutura

A janela principal é composta por quatro áreas.

## Barra Superior

Contém:

- Identificação do WDS.
- Campo de pesquisa.
- Botão Novo Objeto.

**Decisão**: o botão Novo Objeto abre um menu com as quatro formas de
criação já suportadas pelos Services: Importar PDF, Importar Markdown,
Cadastrar Link, Nova Nota. Cada opção aciona o fluxo correspondente
(seletor de arquivo, campo de URL, ou Editor Markdown em branco).

---

## Resultados

Localizado à esquerda.

Responsável por apresentar os objetos encontrados pela pesquisa.

Cada item apresenta:

- título
- tipo
- resumo curto
- tags

Os resultados permanecem estáveis durante toda a navegação.

---

## Objeto em Foco

Localizado à direita.

Sempre existe apenas um objeto em foco.

Apresenta:

- título
- tipo
- data
- tags
- resumo
- pré-visualização

---

## Contexto

Exibe informações relacionadas ao objeto em foco, em duas seções distintas:

### Relacionamentos

Vínculos criados deliberadamente pelo usuário (RelacaoService). Não
possuem score — um relacionamento existe ou não existe, não é uma
medida de parecença.

Cada relacionamento apresenta:

- título
- tipo
- tags
- resumo curto

### Sugestões Semânticas

Objetos ativos automaticamente identificados como semanticamente
parecidos com o objeto em foco, via
`EmbeddingService.buscar_similares_a_objeto`. Cada sugestão exibe um
score de similaridade em percentual, calculado a partir da distância
cosseno já usada em `buscar_semantico`.

O objeto em foco nunca aparece na sua própria lista de sugestões.

Ao selecionar um item, em qualquer uma das duas seções:

- o item selecionado torna-se o novo objeto em foco;
- somente o painel direito é atualizado;
- os resultados da pesquisa permanecem inalterados.

---

# Navegação

Fluxo principal:

Pesquisa

↓

Resultados

↓

Objeto em foco

↓

Contexto

↓

Novo objeto em foco

A pesquisa permanece sendo a âncora da navegação.

---

# Componentes

## Biblioteca

Apresenta todos os Objetos de Conhecimento.

Utiliza os mesmos componentes da pesquisa.

---

## Pesquisa

Permite pesquisa textual e semântica.

---

## Visualização

Apresenta o Objeto de Conhecimento selecionado.

---

## Editor Markdown

Permite edição apenas de notas Markdown.

Não pretende substituir editores especializados.

**Decisão**: toda Nota, seja criada manualmente pelo usuário ou
importada de um arquivo Markdown existente, sempre corresponde a um
arquivo físico real em `acervo/notas/{id}.md`. Uma nota criada pelo
Editor Markdown não permanece apenas como texto no banco de dados —
ela é salva como arquivo desde a primeira gravação, da mesma forma que
uma nota importada. Isso garante que o Editor Markdown sempre edita um
arquivo de verdade, nunca um estado que existe somente no banco.

---

## Lixeira

**Decisão**: tela própria incluída no MVP, não adiada. O backend já
suporta integralmente (`listar_lixeira`, `restaurar`,
`excluir_definitivamente`, todos testados). Reaproveita o mesmo
componente de lista usado na Pesquisa e na Biblioteca, substituindo a
ação padrão de abrir o objeto por duas ações: Restaurar e Excluir
Definitivamente.

---

## Configurações

Centraliza as configurações do sistema.

---

# Integração

A Interface comunica-se exclusivamente com os Services.

Nunca acessa diretamente a camada de Persistência.

**Decisão de padrão arquitetural**: cada `view` possui um `controller`
correspondente (pasta `controllers/`) responsável por mediar a
comunicação com os Services. As `views` nunca chamam um Service
diretamente — sempre passam pelo controller correspondente. Isso
permite testar a lógica de cada tela sem precisar abrir a interface
gráfica, seguindo o mesmo padrão de testabilidade já usado em toda a
camada de Services.

---

# Fora do Escopo

Não fazem parte da Interface do MVP:

- IA generativa
- Chat
- Sugestão automática de relações
- Sugestão automática de tags
- Grafo de conhecimento
- OCR
- Transcrição
- Dashboards analíticos
- Dashboard (adiado para versão posterior ao MVP v1.0.0)

---

# Filosofia

O WDS não navega entre páginas.

O WDS muda apenas o Objeto de Conhecimento em foco.

A pesquisa permanece como âncora da navegação durante toda a sessão.

A interface deve transmitir organização, serenidade e concentração no conhecimento.
