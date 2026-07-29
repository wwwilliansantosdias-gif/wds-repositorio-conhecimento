# WDS â€” Acervo de Conhecimento

WDS Ã© uma aplicaÃ§Ã£o desktop local para preservar, organizar, relacionar e
recuperar conhecimento pessoal. Todo conteÃºdo Ã© registrado como um Objeto de
Conhecimento, independentemente da mÃ­dia.

## VersÃ£o

VersÃ£o em preparaÃ§Ã£o: **v1.0.0 (MVP)**.

## Funcionalidades disponÃ­veis

- cadastro, atualizaÃ§Ã£o, exclusÃ£o lÃ³gica, restauraÃ§Ã£o e exclusÃ£o definitiva
  de Objetos de Conhecimento;
- tags e relacionamentos;
- lixeira;
- pesquisa textual com SQLite FTS5 e pesquisa semÃ¢ntica com ChromaDB;
- importaÃ§Ã£o de PDF, Markdown e DOCX, alÃ©m de cadastro de links;
- editor de notas Markdown;
- biblioteca, configuraÃ§Ãµes, backup, restauraÃ§Ã£o e validaÃ§Ã£o de integridade.

O Dashboard nÃ£o integra o MVP v1.0.0. Ele permanece planejado para uma versÃ£o
posterior.

## Requisitos para executar pelo cÃ³digo-fonte

- Python 3.14;
- dependÃªncias listadas em `requirements.txt`.

InstalaÃ§Ã£o:

```powershell
python -m pip install -r requirements.txt
python app.py
```

## Desenvolvimento e validaÃ§Ã£o

```powershell
python -m unittest discover -s tests -v
python -m compileall -q app.py src
python app.py --check
```

## DocumentaÃ§Ã£o

- `AGENTS.md` â€” regras de desenvolvimento;
- `docs/arquitetura.md` â€” arquitetura oficial;
- `docs/roadmap.md` â€” sequÃªncia oficial de desenvolvimento;
- `docs/docs/issues.md` â€” histÃ³rico e estado das issues.
