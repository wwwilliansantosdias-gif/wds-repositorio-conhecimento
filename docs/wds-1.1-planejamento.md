# WDS 1.1 — Planejamento Técnico

Este documento registra as decisões e o escopo do incremento 1.1,
tomadas em conversa entre Willian e Claude após o fechamento do MVP
1.0. Segue o mesmo espírito de `docs/roadmap.md`: decisões travadas
aqui não devem ser reabertas sem motivo novo.

Princípio geral adotado para todo o 1.1: **caminho mais simples e
seguro, sempre a opção honesta sobre a precisa** quando as duas
divergirem. Nenhum item aqui exige reescrever o projeto — todos se
encaixam no padrão de arquitetura já existente (Services →
Controllers → Views).

---

## 1. Suporte a Planilhas

**Decisão:** seguir o mesmo padrão já usado por PDF/Docx/Markdown em
`ImportacaoService`.

**O que muda:**
- Novo método `extrair_texto_planilha()`, usando `openpyxl` para ler
  células com texto (cabeçalhos e conteúdo textual das colunas —
  não fórmulas nem valores numéricos brutos).
- Novo método `importar_planilha()`, espelhando `importar_pdf()`:
  hash → duplicata → extração → cadastro via `AcervoService` →
  cópia física para `acervo/planilhas/{id}.xlsx`.
- Novo tipo de Objeto: `"Planilha"`.
- `NovoObjetoMenu._importar_arquivo()` ganha `.xlsx` no filtro de
  seleção e no dicionário de importadores.
- `NovoObjetoController` ganha `importar_planilha()`, no mesmo
  padrão de tratamento de erro dos outros três.

**Risco/limite:** só texto de células é indexado para busca. Gráficos,
fórmulas calculadas e formatação não entram no resumo pesquisável.

---

## 2. Suporte a Imagens

**Decisão:** sem OCR. A imagem é armazenada como arquivo físico, e o
texto pesquisável vem de uma descrição digitada manualmente pelo
usuário no momento da importação — não há extração automática de
conteúdo.

**Motivo da escolha:** OCR (ex: `pytesseract`) exigiria instalar um
programa externo (Tesseract), não só uma biblioteca Python, e
aumentaria a superfície de manutenção do projeto sem necessidade
comprovada ainda. Pode ser revisitado em um incremento futuro se a
ausência de OCR se mostrar uma limitação real no uso diário.

**O que muda:**
- Novo tipo de Objeto: `"Imagem"`.
- `NovoObjetoMenu._importar_arquivo()` ganha `.png`, `.jpg`, `.jpeg`
  no filtro. Ao selecionar uma imagem, abre um `DialogoTexto` pedindo
  título e descrição (a descrição vira o resumo pesquisável) —
  mesmo padrão já usado em `_cadastrar_link()`.
- `ImportacaoService.importar_imagem()`: sem etapa de extração de
  texto, copia o arquivo para `acervo/imagens/{id}.{extensao}`.
- **`ObjetoView` precisa de um componente novo** para exibir a
  miniatura da imagem no painel (`CTkImage`, do CustomTkinter) —
  hoje a view só sabe renderizar texto. Isso é o item de maior
  esforço deste ponto.

---

## 3. Painel fixo de Tags

**Decisão:** painel/lista sempre visível (não só dentro do objeto
selecionado), reaproveitando o método que já existe e nunca foi
conectado a uma tela: `TagController.listar_todas()`.

**O que muda:**
- Novo widget de listagem de tags, usado numa nova coluna (ou painel
  retrátil) na janela principal — hoje `main_window.py` só tem duas
  colunas (Resultados e Objeto em Foco).
- Clicar numa tag do painel dispara a mesma busca textual que já
  existe hoje ao clicar numa tag dentro do objeto
  (`_ao_selecionar_tag` → `pesquisa_view.pesquisar(nome_tag)`) —
  nenhuma lógica de busca nova, só uma nova porta de entrada para a
  que já existe.

**Risco/limite:** nenhum — é composição de peças já existentes e
testadas (`TagService.listar()`, fluxo de busca por tag já em
produção).

---

## 4. Busca semântica também pelas Tags

**Problema encontrado na auditoria desta conversa:** hoje,
`TagController.adicionar_tag()` e `remover_tag()` chamam
`TagService` diretamente. `TagService` só mexe no SQLite — nunca
passa pelo `AcervoService`, que é quem dispara o reindexamento
semântico (`EmbeddingService.indexar_objeto`). Resultado: adicionar
ou remover uma tag **nunca atualiza o vetor semântico do objeto**,
mesmo que isso mude o contexto dele.

**Decisão:** ao adicionar ou remover uma tag, reindexar o objeto
incluindo os nomes das tags atuais no texto usado para gerar o
vetor, no formato:

```
{titulo}
{resumo}
Tags: {tag1}, {tag2}, ...
```

**O que muda:**
- `TagController` passa a receber também `AcervoService` (hoje só
  recebe `TagService` e `ObjetoService`).
- Após `associar()`/`desassociar()`, o controller busca o objeto
  atualizado e as tags atuais, monta o texto acima, e chama
  `acervo_service.atualizar(...)` para disparar o reindexamento.
- `main_window.py` precisa passar `acervo_service` na criação do
  `TagController`.

**Risco/limite:** nenhum estrutural — é uma correção de um
comportamento que já deveria existir, não uma feature nova de
verdade. Efeito colateral esperado e desejado: buscas semânticas por
palavras relacionadas ao *significado* de uma tag (ex.: buscar
"finanças" e encontrar objetos com a tag "orçamento") passam a
funcionar.

---

## 5. Mostrar o trecho que justifica o score da busca

Este item tem duas metades com dificuldade bem diferente. Tratadas
separadamente e de forma honesta quanto ao que cada uma realmente
entrega.

### 5a. Busca textual (fácil — entra no 1.1)

**Decisão:** usar a função nativa do SQLite `snippet()` no FTS5, que
já devolve automaticamente o trecho do texto que bateu com o termo
buscado, com marcação do trecho relevante.

**O que muda:**
- `PesquisaService.buscar_texto()` passa a selecionar também
  `snippet(tabela_objetos_fts, ...)` junto com os campos já
  existentes.
- `ResultadoPesquisa` (em `PesquisaController`) ganha um campo novo,
  `trecho: str | None`.
- `ResultadoItem` (widget) exibe esse trecho quando presente.

### 5b. Busca semântica (difícil — **fora do 1.1**, ver honestidade abaixo)

**Por que não entra ainda, dito sem rodeio:** hoje cada objeto vira
**um único vetor** (título + resumo inteiro). O score é do texto
inteiro — não existe, na estrutura atual, "a frase que causou o
score". Mostrar um trecho de verdade exigiria dividir cada objeto em
pedaços menores (parágrafos), cada um virando seu próprio vetor, e
mudar a busca para comparar contra pedaços — uma mudança estrutural
grande em `EmbeddingService` (de "1 vetor por objeto" para "N
vetores por objeto"), fora do critério de "caminho mais simples e
seguro" combinado para este incremento.

**Solução adotada para o 1.1, honesta sobre o que é:** mostrar o
início do resumo do objeto como "contexto", **rotulado como tal**
("Contexto:", não "Trecho encontrado:") — sem prometer que aquele
pedaço específico foi o responsável pelo percentual de similaridade,
porque isso não seria verdade. Fica pendente para um 1.2 avaliar se
vale a pena o esforço maior do chunking.

---

## 6. Acesso ao arquivo original

**Decisão:** botão simples ao lado de "Mover para Lixeira", em
`ObjetoView`, que abre o arquivo físico (ou a URL, no caso de Link)
no programa padrão do sistema.

**O que muda:**
- `Objeto.caminho` já guarda o caminho físico ou a URL — nenhum dado
  novo precisa ser criado, o campo já existe e já é preenchido pela
  importação.
- Novo botão "Abrir Original" em `ObjetoView`, ao lado do botão de
  lixeira.
- Lógica de abertura: `os.startfile(caminho)` para arquivos locais
  (Windows); `webbrowser.open(caminho)` quando o tipo do objeto for
  `"Link"`.
- Objetos do tipo `"Nota"` não precisam do botão — já têm o Editor
  Markdown para isso.

**Risco/limite:** nenhum — é o item de menor esforço deste
documento, só falta a interface.

---

## Ordem sugerida de implementação

1. Acesso ao arquivo original (6) — esforço mínimo
2. Trecho do score na busca textual (5a)
3. Planilhas (1)
4. Painel fixo de tags (3)
5. Tags no vetor semântico (4)
6. Imagens (2)

Chunking para trecho semântico (5b) fica fora do 1.1, candidato a
1.2.
