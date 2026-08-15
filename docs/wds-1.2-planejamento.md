# WDS 1.2 — Planejamento Técnico

Registra o escopo do incremento 1.2, decidido em conversa entre
Willian e Claude após o fechamento do 1.1. Segue o mesmo formato e
espírito de `wds-1.1-planejamento.md`: decisões travadas aqui não
devem ser reabertas sem motivo novo.

Duas frentes independentes entre si (nenhuma depende da outra
tecnicamente), reunidas num só documento porque foram decididas na
mesma conversa e fecham o mesmo incremento.

**Fora do 1.2, por decisão explícita:** captura rápida via
n8n/Telegram/WhatsApp fica guardada, não entra neste incremento.
Transcrição automática de áudio/vídeo (Whisper embutido no WDS)
continua descartada — a transcrição acontece fora do WDS, por
escolha deliberada, e o resultado entra como Nota comum.

---

# Parte A — Navegação Associativa

Objetivo: aproximar a navegação de um fluxo de pensamento/lembrança,
não uma ficha estática por objeto. Passou por auditoria de duas
rodadas antes de fechar; onde algo mudou de uma primeira ideia, está
anotado.

## A.0 — Criar Relacionamento (pré-requisito de tudo em Parte A)

**Decisão:** interação inline, mesmo padrão já usado por "+ tag" —
sem modal, sem trocar de contexto.

**Fluxo:**
1. Botão "+ Relacionar" no cabeçalho de Objeto em Foco, ao lado de
   Editar/Abrir Original/Mover para Lixeira, visível para qualquer
   tipo de objeto.
2. Campo de busca inline ao clicar, reaproveitando a busca textual
   já existente (`PesquisaService`) — sem mecanismo de busca novo.
3. Se a busca não encontrar nada: oferecer "Criar novo objeto:
   '{texto digitado}'" na própria lista de resultados — cria como
   Nota em branco com esse título, sem abandonar o fluxo.
4. Campo de "tipo de relação" **em texto livre**, com autocompletar
   reaproveitando tipos já usados antes (mesmo padrão de tags:
   reaproveita se existe, cria se não existe). Precisa de um método
   novo de leitura em `RelacaoService`
   (`listar_tipos_distintos()`), só leitura, sem mudança de schema.
   Lista fixa de tipos foi descartada deliberadamente.
5. Confirmar cria o `Relacao` e o item aparece na lista
   imediatamente.

**Rótulo assimétrico, resolvido sem campo extra:** um relacionamento
tem um único rótulo, mostrado igual dos dois lados, mesmo que leia
de forma gramaticalmente imperfeita de um dos lados (ex.:
"Transcrição de" faz sentido pela Nota, não pelo Vídeo). Decisão:
aceitar essa imprecisão — o título do objeto do outro lado já
carrega o contexto real, não precisa de um segundo campo de "rótulo
invertido".

## A.1 — Trilha associativa

Trilha visível de por onde a navegação passou dentro de Objeto em
Foco, cada ponto clicável para voltar até ali (comportamento de
breadcrumb, descarta o que vinha depois ao clicar no meio).

Cresce **somente** quando o clique nasce dentro das seções de
Contexto (Relacionamentos ou Sugestões Semânticas); reinicia para
qualquer outra forma de chegar a um objeto (Pesquisa, Biblioteca,
painel de Tags, criação de objeto novo).

Mecanismo contido inteiramente em `ObjetoView`: os itens do Contexto
passam a usar um wrapper interno (registra o objeto atual na trilha,
depois chama o callback externo normalmente) em vez do callback
externo direto; `mostrar_objeto()` reinicia a trilha por padrão, a
não ser que a chamada tenha vindo desse wrapper (um flag interno
consumido uma vez resolve isso). Nenhum callback usado por fora de
`ObjetoView` muda de assinatura.

## A.2 — Peso visual por força da associação

Só se aplica a Sugestões Semânticas (Relacionamentos são
deliberados, ficam com peso uniforme).

Mecanismo por **cor/opacidade**, reaproveitando a linguagem visual
já existente no app (`gray60` para texto secundário), não por
tamanho de fonte (descartado — risco de parecer bug de layout, e
desloca altura de linha):
- score ≥ 75: cor de destaque (tom mais vivo, eventualmente um toque
  do teal já usado nas tags).
- 50 ≤ score < 75: peso atual, sem mudança.
- score < 50: mais apagado que o `gray60` de hoje.

Não afeta a lista de Resultados da Pesquisa.

## A.3 — Menos itens abertos por padrão

Tratamento diferente por seção, ajustado na auditoria (a primeira
versão cortava as duas igual):

- **Sugestões Semânticas**: geradas automaticamente, podem virar
  ruído. Exibir só as 2-3 mais fortes por padrão, "Ver mais" revela
  o resto (já carregado, sem busca nova).
- **Relacionamentos**: deliberados, tendem a ser poucos, esconder
  algo registrado conscientemente vai contra a ideia de lembrança
  ativa. **Sempre aparecem inteiros, sem corte.**

## Candidato futuro (Parte A), fora deste escopo

**Trilha repetida como memória formada sozinha.** Se o mesmo par de
objetos for percorrido repetidamente ao longo do tempo pela Trilha
(A.1), isso é sinal de conexão mais parecido com memória de verdade
do que um Relacionamento manual. Exige schema novo (registrar e
contar travessias ao longo do tempo) e validação de que esse padrão
de uso aparece na prática antes de justificar o esforço. Anotado
para avaliação futura, não para implementação agora.

---

# Parte B — Áudio e Vídeo (catálogo, sem transcrição)

Objetivo: catalogar arquivos de áudio e vídeo no acervo, mesmo
padrão já usado para Imagem — sem extrair conteúdo automaticamente.
Transcrição continua um passo manual, feito fora do WDS, cujo
resultado entra como Nota comum e se conecta ao objeto de
áudio/vídeo via Relacionamento (Parte A.0).

**Mais simples que Imagem, não mais complexo:** não precisa de
nenhuma biblioteca nova (Imagem precisou de Pillow para a miniatura;
aqui não há preview nenhum para gerar) e não precisa de widget de
visualização novo — "Abrir Original" (já existente) já abre o
arquivo no player padrão do sistema.

**O que muda:**
- Dois tipos de Objeto novos: `"Audio"` e `"Video"` (tipos
  separados, não um tipo combinado — mesmo padrão já usado para
  distinguir PDF de Documento de Planilha de Imagem).
- `ImportacaoService` ganha `importar_audio()` e `importar_video()`,
  espelhando `importar_imagem()`: hash → duplicata → **descrição
  obrigatória** (mesma validação de Imagem: sem extração automática,
  a descrição é o único texto pesquisável) → cadastro via
  `AcervoService` → cópia para `acervo/audio/{id}{extensao}` ou
  `acervo/videos/{id}{extensao}` (extensão original preservada, para
  o player do sistema reconhecer o formato) → atualização do
  caminho definitivo.
- Extensões cobertas: sugestão inicial `.mp3 .wav .m4a .ogg` para
  áudio, `.mp4 .mov .avi .mkv` para vídeo — ajustável, não é decisão
  travada.
- `NovoObjetoMenu`/`NovoObjetoController`: mesmo padrão de
  integração já usado para Planilha e Imagem (filtro de arquivo,
  diálogo pedindo título opcional + descrição).
- `.gitignore` e `docs/arquitetura.md`: novas pastas
  `acervo/audio/.gitkeep` e `acervo/videos/.gitkeep`, mesmo padrão
  das demais. Atenção à ordem alfabética na árvore de pastas do
  `arquitetura.md` desta vez (`audio` vem antes de `documentos`).

**Consideração de tamanho, não bloqueante:** arquivos de áudio e,
principalmente, vídeo tendem a ser muito maiores que PDF ou imagem.
Isso engorda `acervo/` e, por consequência, todo `.zip` gerado pelo
Backup. Não muda a decisão de fazer, só é bom ter em mente ao
acompanhar o tamanho dos backups depois.

---

# Ordem sugerida de implementação (1.2 inteiro)

1. **A.0 — Criar Relacionamento.** Pré-requisito de A.1 e A.3.
2. **Parte B — Áudio e Vídeo.** Independente de tudo em Parte A,
   pode entrar em paralelo ou logo em seguida — mesmo padrão já
   validado em Planilha e Imagem, baixo risco.
3. **A.1 — Trilha associativa.**
4. **A.3 — Menos itens por padrão.**
5. **A.2 — Peso visual por score.** O mais cosmético, mais legível
   depois do corte do item A.3 já estar em vigor.
