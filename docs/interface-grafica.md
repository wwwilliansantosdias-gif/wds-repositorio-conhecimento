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

Exibe os relacionamentos cadastrados para o objeto em foco.

Cada relacionamento apresenta:

- título
- tipo
- tags
- resumo curto

Ao selecionar um relacionamento:

- o relacionamento torna-se o novo objeto em foco;
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

## Dashboard

Tela inicial.

Apresenta acesso rápido às funcionalidades.

---

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

---

## Configurações

Centraliza as configurações do sistema.

---

# Integração

A Interface comunica-se exclusivamente com os Services.

Nunca acessa diretamente a camada de Persistência.

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

---

# Filosofia

O WDS não navega entre páginas.

O WDS muda apenas o Objeto de Conhecimento em foco.

A pesquisa permanece como âncora da navegação durante toda a sessão.

A interface deve transmitir organização, serenidade e concentração no conhecimento.