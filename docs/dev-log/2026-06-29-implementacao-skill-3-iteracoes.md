# 2026-06-29 — Implementação da skill: 3 iterações validadas em contexto limpo

**Iteração:** #1–3 · **Projeto(s):** code-smells-project · ecommerce-api-legacy · task-manager-api

## O que mudou

- **Skill `refactor-arch` autorada** (3 fases como steps + progressive disclosure para os
  reference files): `SKILL.md` (3 fases) +
  5 reference files (`analysis`, `anti-patterns` com 19 entradas + APIs deprecated,
  `report-template`, `mvc-guidelines`, `playbook` com 11 transformações) + `sync-skill.sh`.
- **3 projetos refatorados para MVC** in-place, cada um com harness de caracterização +
  baseline, e relatório de auditoria. Reports agregados em `reports/audit-project-{1,2,3}.md`.
- **3 iterações da skill** (v1→v2→v3) — ver abaixo.

## Por quê

O risco central (ADR-0001) é a skill acoplar a um projeto. Para *provar* agnosticidade
(não afirmar), o loop foi **invertido**: cada projeto foi rodado por um **agente em
contexto limpo**, escopado ao diretório do projeto e proibido de ler qualquer doc de
planejamento — o cenário do avaliador. Cada run cold também reportou **onde a skill
falhou**, alimentando as iterações:

- **v2 (gaps do P1):** régua de severidade não viajava na cópia → inlinada; gate de
  status-class forçava manter vuln aberta → exceção de hardening intencional (re-baseline);
  harness sem `Content-Type` dava 415→500.
- **v3 (gaps do P2/P3):** boot por subprocess quando o app não é importável; semear antes
  do baseline; corpo array/texto; GREEN cobre só o caminho feliz; `crypto.scrypt` stdlib.

## Resultado da validação

Todos GREEN; cada refatoração passou ainda por um verificador **adversarial** independente.

| Projeto | Fase 1 stack | Fase 2 ≥5 findings | ≥1 CRIT/HIGH | Fase 3 app de pé |
|---|:--:|:--:|:--:|:--:|
| code-smells-project | ✅ Python/Flask | ✅ 17 | ✅ 5C | ✅ harness GREEN (19 ep) |
| ecommerce-api-legacy | ✅ Node/Express | ✅ 15 | ✅ 4C | ✅ harness GREEN (3 ep) · verify PASS |
| task-manager-api | ✅ Python/Flask | ✅ 13 | ✅ 3C | ✅ harness GREEN (22 ep) · verify PASS |

## Pendências / próximos passos

- Gaps menores conhecidos da skill (não-bloqueantes, registrados pelos runs cold):
  enforcement da pausa da Fase 2 depende do host; o GREEN narrow após re-baseline atesta
  só os endpoints não-rebaselinados. Candidatos a uma eventual v4 se um run futuro exigir.
- P3 deixou `utils/helpers.py` como código morto (mudança mínima e segura) e
  `delete_category` sem cascade — registrados como achados, fora do escopo refatorado.
