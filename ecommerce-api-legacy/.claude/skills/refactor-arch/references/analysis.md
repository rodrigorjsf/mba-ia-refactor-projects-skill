# Análise — heurísticas de detecção e mapeamento

Fase 1. Detecte a stack por **manifestos e imports**, não por chute. Depois mapeie a arquitetura e o route map.

## Linguagem + gerenciador de pacotes

| Sinal (arquivo na raiz) | Linguagem | Ecossistema |
|---|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `*.py` | Python | pip/poetry |
| `package.json`, `*.js`, `*.ts` | Node.js | npm/yarn |
| `go.mod` | Go | go modules |
| `pom.xml`, `build.gradle` | Java | maven/gradle |

A versão da linguagem/deps sai do manifesto (ex: `flask==3.1.1` em `requirements.txt`; `"express": "^4.18.2"` em `package.json`).

## Framework web

Detecte pelos imports/dependências, não pelo nome da pasta:

- **Flask** — `from flask import Flask`; rotas via `@app.route`, `app.add_url_rule` ou `Blueprint`.
- **Express** — `require('express')` / `import express`; rotas via `app.get/post/...` ou `Router`.
- **FastAPI** — `from fastapi import FastAPI`; rotas via `@app.get`.
- **Django** — `urls.py` + `INSTALLED_APPS`.

## Banco de dados

- **SQLite** — `sqlite3.connect(...)` (Python), `require('sqlite3')` (Node), `sqlite:///...` (SQLAlchemy URI).
- **ORM** — SQLAlchemy (`db.Column`, `db.Model`), Sequelize, Prisma. Sem ORM = SQL cru (procure `cursor.execute`, `db.run/get/all`).
- **Tabelas/coleções** — extraia dos `CREATE TABLE`, das classes de model (`__tablename__`) ou das migrations.

## Domínio do negócio

Inferido dos nomes de tabela, rota e entidade. Descreva em uma frase: ex. "API de e-commerce (produtos, pedidos, usuários)", "LMS com checkout (cursos, matrículas, pagamentos)", "gerenciador de tarefas (tasks, usuários, categorias)".

## Mapeamento de arquitetura

Classifique cada arquivo-fonte numa camada (ou marque como não-separado):

- **Monólito** — tudo em poucos arquivos, sem camadas (ex: lógica + SQL + rota no mesmo arquivo).
- **Parcialmente organizado** — já há `models/`, `routes/`, `services/`, mas com vazamentos (lógica na rota, segredo no código, model anêmico).

Conte os arquivos-fonte reais (exclua deps, banco, venv) e reporte o número.

## Route map (insumo do harness)

Liste todos os endpoints como `MÉTODO /path`. Fontes, em ordem de confiança:

1. Registro de rotas no entry point (`app.add_url_rule`, `@app.route`, `app.get(...)`, `register_blueprint` → abrir os blueprints).
2. Arquivo `api.http` / coleção de requests, se houver — também dá os payloads representativos.
3. Decorators/handlers espalhados pelos arquivos de rota.

Para cada endpoint mutante (POST/PUT/DELETE), derive o **payload mínimo** que passa nas validações do handler (campos obrigatórios + valores válidos). Esse route map alimenta o harness de caracterização da Fase 1.

## Formato do resumo (Fase 1)

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem + versão>
Framework:     <framework + versão>
Dependencies:  <principais>
Domain:        <uma frase>
Architecture:  <monólito | parcialmente organizado — descrição>
Source files:  <N> files analyzed
DB tables:     <lista>
Endpoints:     <N> rotas mapeadas
================================
```
