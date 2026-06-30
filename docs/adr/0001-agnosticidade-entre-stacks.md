---
status: accepted
---

# Uma única skill agnóstica de stack, com detecção + transformações específicas por stack

## Contexto

O critério de aceite do SPEC é **OBRIGATÓRIO nos 3 projetos** (2 Python/Flask + 1
Node/Express, em níveis diferentes de organização). A skill `refactor-arch` é uma só
e copiada para dentro de cada projeto — não pode haver uma variante por linguagem.

## Decisão

A skill é **agnóstica de stack por design**: a Fase 1 detecta a stack (linguagem,
framework, banco) por heurísticas, e o catálogo/playbook expressam cada anti-pattern
e cada transformação de forma **dupla** — um princípio agnóstico (ex: "nunca concatene
input em query") com exemplos concretos **por stack** (Flask/SQLite e Express/SQLite).
A Fase 3 escolhe a transformação concreta conforme a stack detectada. Nada no SKILL.md
é hardcoded para um projeto específico.

## Consequências

- Estrutura dos reference files segue esse eixo: catálogo e playbook organizados por
  anti-pattern, com blocos antes/depois por stack — não um arquivo por projeto.
- O harness de validação (ver [ADR-0003](./0003-validacao-harness-como-gate-tdd.md))
  opera no nível HTTP justamente para ser agnóstico.
- "Funciona nos 3" é uma propriedade **provada** pelo harness, não afirmada.
- Risco principal do projeto. Se a skill ficar acoplada a um projeto, falha o aceite —
  por isso a validação roda nos 3 antes de declarar pronto.
