# Criação de Skills — Refatoração Arquitetural Automatizada

Skill `refactor-arch`: uma Skill do Claude Code que **analisa, audita e refatora**
qualquer projeto para o padrão **MVC**, de forma **agnóstica de tecnologia**.
Projeto do MBA em Engenharia de Software com IA — desafio descrito em
[`docs/SPEC.md`](docs/SPEC.md).

> **Status:** planejamento concluído · implementação em andamento. Acompanhe o
> [`docs/ROADMAP.md`](docs/ROADMAP.md). Decisões em [`docs/adr/`](docs/adr/),
> vocabulário em [`CONTEXT.md`](CONTEXT.md).

<!-- TODO(Fase 4): manter este README em sync com o código no MESMO commit que muda comportamento. Ver docs/DOCUMENTACAO.md -->

## Sumário

- [Visão geral](#visão-geral)
- [A) Análise Manual](#a-análise-manual)
- [B) Construção da Skill](#b-construção-da-skill)
- [C) Resultados](#c-resultados)
- [D) Como Executar](#d-como-executar)

## Visão geral

A skill roda em 3 fases sequenciais:

1. **Análise** — detecta stack (linguagem, framework, banco) e mapeia a arquitetura.
2. **Auditoria** — cruza o código com um catálogo de anti-patterns, gera um relatório
   por severidade e **pausa pedindo confirmação**.
3. **Refatoração** — reestrutura para MVC e **valida** que a aplicação continua de pé.

Projetos-alvo do desafio:

| Projeto | Stack | Domínio |
|---|---|---|
| `code-smells-project` | Python/Flask | E-commerce API |
| `ecommerce-api-legacy` | Node/Express | LMS API com checkout |
| `task-manager-api` | Python/Flask | Task Manager (parcialmente organizado) |

---

## A) Análise Manual

_(a preencher na Fase 1 — ver [ROADMAP §Fase 1](docs/ROADMAP.md#fase-1--análise-manual-dos-3-projetos-spec-1))_

Para cada projeto: ≥5 problemas, sendo ≥1 CRITICAL/HIGH, ≥2 MEDIUM, ≥2 LOW, com
**classificação por severidade** e **justificativa** de por que cada um importa.

### code-smells-project

| # | Severidade | Problema | Arquivo:linha | Por que importa |
|---|---|---|---|---|
| | | <!-- TODO --> | | |

### ecommerce-api-legacy

| # | Severidade | Problema | Arquivo:linha | Por que importa |
|---|---|---|---|---|
| | | <!-- TODO --> | | |

### task-manager-api

| # | Severidade | Problema | Arquivo:linha | Por que importa |
|---|---|---|---|---|
| | | <!-- TODO --> | | |

---

## B) Construção da Skill

_(a preencher na Fase 2)_

- **Decisões de design** — como SKILL.md e os reference files foram estruturados.
  Ver [`docs/adr/`](docs/adr/).
- **Anti-patterns do catálogo** — quais entraram e por quê.
- **Agnosticidade de tecnologia** — como a skill funciona nas 3 stacks
  ([ADR-0001](docs/adr/0001-agnosticidade-entre-stacks.md)).
- **Desafios** — o que deu trabalho e como foi resolvido (puxar do dev-log).

---

## C) Resultados

_(a preencher na Fase 3/4)_

### Resumo dos relatórios de auditoria

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|:--:|:--:|:--:|:--:|:--:|
| code-smells-project | | | | | |
| ecommerce-api-legacy | | | | | |
| task-manager-api | | | | | |

### Antes / depois da estrutura

<!-- TODO: árvore de diretórios antes vs depois por projeto (snapshot 'antes' da Fase 3) -->

### Checklist de Validação preenchido

<!-- TODO: colar o checklist preenchido por projeto. Modelo em docs/ROADMAP.md -->

### Apps rodando após refatoração

<!-- TODO: logs/screenshots do boot + endpoints respondendo -->

### Observações por stack

<!-- TODO: como a skill se comportou em Flask vs Express -->

---

## D) Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e configurado
- Python 3.12+ (projetos Flask) e Node.js (projeto Express)

### Rodar a skill em cada projeto

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

A saída da Fase 2 de cada projeto é salva em `reports/audit-project-{1,2,3}.md`.

### Validar a refatoração

<!-- TODO(Fase 3): comandos de boot + smoke de cada app refatorada -->
