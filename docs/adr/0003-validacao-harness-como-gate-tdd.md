---
status: accepted
---

# Validação por harness de caracterização gerado pela skill, como gate de TDD

## Contexto

O `CLAUDE.md` exige TDD (red-green-refactor) em toda mudança, mas a skill é Markdown e
os 3 projetos-alvo não têm teste algum. O SPEC, por sua vez, exige que a Fase 3 prove
"app sobe + endpoints respondem". São o mesmo problema.

## Decisão

A skill **gera, na Fase 1, um harness de caracterização (smoke)** a partir do route map:
sobe o app, bate em todos os endpoints (GET completos; payloads mínimos representativos
para POST/PUT/DELETE, inferidos das validações do código ou do `api.http`), e grava o
baseline (status + shape) **antes** de qualquer mudança. Esse baseline é a peça "red" do
TDD — o contrato que a refatoração não pode quebrar. A Fase 3 re-roda o harness e exige
verde. O harness e o baseline são salvos dentro do projeto para reprodutibilidade.

## Consequências

- O harness opera no nível HTTP → agnóstico de stack (casa com
  [ADR-0001](./0001-agnosticidade-entre-stacks.md)).
- "TDD obrigatório" do `CLAUDE.md` é honrado: o baseline-antes é o teste que gate a
  refatoração; nenhuma mudança de Fase 3 é aceita sem o harness verde.
- Não escrevemos suíte unitária por camada nos 3 projetos — seria over-engineering e não
  prova mais do que "os endpoints originais respondem".
- Campos voláteis (timestamps, ids autogerados) são comparados por shape/classe de
  status, não por igualdade exata.
- O harness deve **neutralizar efeitos colaterais externos reais** antes de bater nos
  endpoints — ex: `task-manager-api/services/notification_service.py` faz chamada
  `smtplib` viva ao Gmail ao atribuir uma task. Sem stub/mock do SMTP o baseline fica
  lento, flaky e não-determinístico.
