# WDS — Acervo de Conhecimento

WDS é uma aplicação desktop local para preservar, organizar, relacionar e
recuperar conhecimento pessoal. Todo conteúdo é registrado como um Objeto de
Conhecimento, independentemente da mídia.

## Versão

**v1.0.0** — lançada.

## Funcionalidades disponíveis

- cadastro, atualização, exclusão lógica, restauração e exclusão definitiva
  de Objetos de Conhecimento;
- tags e relacionamentos;
- lixeira;
- pesquisa textual com SQLite FTS5 e pesquisa semântica com ChromaDB;
- importação de PDF, Markdown e DOCX, além de cadastro de links;
- editor de notas Markdown;
- biblioteca, configurações, backup, restauração e validação de integridade.

O Dashboard não integra o MVP v1.0.0. Ele permanece planejado para uma versão
posterior (ver `docs/wds-1.1-planejamento.md` para o escopo já definido do
próximo incremento).

## Requisitos para executar pelo código-fonte

- Python 3.14;
- dependências listadas em `requirements.txt`.

Instalação:

```powershell
python -m pip install -r requirements.txt
python app.py
```

## Abrir sem usar o terminal

O arquivo `Abrir WDS.bat`, na raiz do projeto, inicia o programa via `pyw`
(sem abrir janela de terminal). Para um ícone clicável na Área de Trabalho:
clique com o botão direito em `Abrir WDS.bat` → "Enviar para" → "Área de
trabalho (criar atalho)".

Não há instalador formal (`.exe`) para esta versão -- ver `docs/issues.md`,
Issue 32, para o motivo dessa decisão.

## Desenvolvimento e validação

```powershell
python -m unittest discover -s tests -v
python -m compileall -q app.py src
```

## Documentação

- `AGENTS.md` — regras de desenvolvimento;
- `docs/arquitetura.md` — arquitetura oficial;
- `docs/roadmap.md` — sequência oficial de desenvolvimento;
- `docs/issues.md` — histórico e estado das issues;
- `docs/wds-1.1-planejamento.md` — escopo definido do próximo incremento.
