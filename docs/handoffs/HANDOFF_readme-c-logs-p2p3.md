# Handoff: corrigir o único drift do review — logs de P2/P3 no README §C

**Criado:** 2026-06-30
**Branch:** `main` (working tree limpo, sincronizado com `origin/main`)
**Origem:** workflow de review completo contra o SPEC (12 agentes especializados por categoria)

---

## Summary

A entrega da skill `refactor-arch` está **substancialmente completa e validada**: review apurou **83/85 requisitos do SPEC**, com os **4 critérios de aceite OBRIGATÓRIOS cumpridos em 3/3 projetos** e **confirmados adversarialmente** (boots reais, harness GREEN, EXIT 0 em P1/P2/P3). Resta **1 drift documental** a corrigir: a seção C do README só exibe o **log real do harness do P1**; **P2 e P3** estão cobertos apenas por uma frase em prosa. O SPEC exige "Screenshots ou logs mostrando **as aplicações** rodando após refatoração" (plural → os 3). Esta é a única ação pendente para fechar 85/85.

> Relatório de review completo (evidência por requisito): [`docs/review/2026-06-29-review-completo-spec.md`](../review/2026-06-29-review-completo-spec.md) — commit `0f5b1b4`.

---

## O drift a corrigir (único, bloqueante p/ 100%)

- **Onde:** `README.md`, seção **C) Resultados** → subseção `### Apps rodando após refatoração (harness)` (a partir da **linha 267**; bloco do P1 na linha ~271).
- **Estado atual:** só o **P1** tem bloco de código com saída real (`captured 19 endpoints ... GREEN`). Logo depois há uma frase em prosa: _"P2 (`node harness/run.js verify`) e P3 (`PYTHONPATH=. python harness/characterize.py ... --compare`) re-rodaram **GREEN** da mesma forma..."_ — **sem bloco de log para P2 e P3**.
- **O que o SPEC pede** (`docs/SPEC.md`, seção "README.md deve conter" → C): "Screenshots ou logs mostrando as aplicações rodando após refatoração" — para os 3 projetos.
- **Correção:** adicionar **blocos de log reais** do harness de **P2** e **P3** logo após o bloco do P1, mantendo a nota da verificação adversarial. Substituir a frase em prosa pelos blocos + uma linha de introdução.

---

## Immediate Next Steps (comece aqui)

### 1. Gerar a saída real do harness do P2 (Node/Express)

```bash
cd ecommerce-api-legacy
npm install
node harness/run.js verify
```

**Saída esperada** (capturada pelos verificadores adversariais nesta sessão — deve reproduzir):

```
GREEN POST /api/checkout              base=2xx(200) now=2xx(200)
GREEN GET  /api/admin/financial-report base=2xx(200) now=2xx(200)
GREEN DELETE /api/users/:id           base=4xx(401) now=4xx(401)
RESULT: GREEN
```
(EXIT_CODE=0; `DELETE` é 401 por hardening de auth — re-baseline documentado.)

### 2. Gerar a saída real do harness do P3 (Flask parcial)

```bash
cd task-manager-api
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python seed.py
PYTHONPATH=. .venv/bin/python harness/characterize.py harness/postrefactor.json --compare harness/baseline.json
```

**Saída esperada:** `RESULT: GREEN`, EXIT=0, **22/22 endpoints 2xx**; o compare reporta `removed top keys [password]` em `GET /users/1`, `POST /users`, `PUT /users/2` (PII removido vs baseline).

### 3. Editar `README.md` §C

Na subseção `### Apps rodando após refatoração (harness)` (linha 267), **depois** do bloco do P1, **substituir a frase em prosa** ("P2 ... e P3 ... re-rodaram GREEN da mesma forma...") por:

- um bloco ```` ```text ```` com a saída real do P2 (passo 1);
- um bloco ```` ```text ```` com a saída real do P3 (passo 2);
- manter a frase final sobre a **verificação adversarial independente (ambos PASS)**.

Manter o bloco do P1 como está. Não inflar — 3 blocos curtos + 1 linha de contexto cada.

### 4. Commitar (docs-only)

```bash
git add README.md
git commit -m "docs(readme): adiciona logs reais do harness de P2 e P3 na secao C" \
  -m "Fecha o unico drift do review vs SPEC: a secao C exige logs das aplicacoes
rodando apos refatoracao para os 3 projetos; antes so o P1 tinha bloco real." \
  -m "Claude-Session: https://claude.ai/code/session_01DH9Qv9fau42aTZx4Xbxrm3"
git push origin main
```

ROADMAP **não** precisa mudar (sem mudança de comportamento; é só evidência no README). README já está marcado entregue no ROADMAP.

### 5. Re-validar o fechamento do gap

Confirmar que a §C do README agora tem **3 blocos de log** (P1/P2/P3). Opcional: re-rodar só a dimensão `readme-content` do workflow de review (era a única em `FAIL`) para confirmar que vira `PASS` → 85/85.

---

## Current State

### What's Working (não mexer)

- **Skill `refactor-arch`** (v3): `SKILL.md` 3 fases + 5 reference files (catálogo **19** anti-patterns + APIs deprecated, playbook **11** transformações, dual-stack). Idêntica (md5sum) nos 3 projetos. Canônica na raiz `.claude/skills/` (gitignored); cópias dos projetos rastreadas (ADR-0002).
- **P1/P2/P3 refatorados para MVC**, harness GREEN, verificação adversarial **CONFIRMED**. Commits `80b16ac` (P1), `cc1fea7` (P2), `d91f929` (P3).
- **Relatórios** em `reports/audit-project-{1,2,3}.md`. **README A/B/D** completos. **Issues** #1–#6 fechados. Repo **público + fork**.

### Ressalva conhecida (⚠️ NÃO é drift — não corrigir)

- **P1 `/admin/query`→404 e `/admin/reset-db`→401:** mudança de classe de status **mandatada pelo SPEC** (Fase 3 = "eliminar os achados"; `/admin/query` é o CRITICAL de SQL arbitrário). Re-baselinada e documentada (`code-smells-project/harness/baseline.json` + report FASE 3 + `mvc-guidelines.md` › exceção). O review classificou como ⚠️, não ❌.

### Polish opcional (não-bloqueante, fora dos critérios de aceite)

- **P3:** `datetime.utcnow()` ainda presente em `task-manager-api/seed.py` (5×) e `utils/helpers.py:38` (1×) — a modernização foi aplicada nos models/controllers mas não no seed/helper. App sobe GREEN; é higiene, não aceite.
- Relatórios duplicados (raiz `reports/` + `<projeto>/reports/`): proposital (provenance); pode-se manter.

---

## Things to Know

- **Não refatorar contaminado:** a prova de agnosticidade veio de rodar a skill em **contexto limpo** (subagentes escopados ao projeto). Para o fix do README isso é irrelevante (é só colar log real), mas não "reescreva" os projetos.
- **Harness self-referential nos endpoints re-baselinados:** o GREEN prova preservação de classe de status para os endpoints não-rebaselinados; os 2 admin do P1 foram re-baselinados de propósito. Já documentado.
- **Idioma:** todos os artefatos do repo em **pt-BR** (override do projeto); só o `CLAUDE.md` fica em inglês. Nunca citar a skill de autoria de skills diretamente em docs — só os conceitos.
- **Commits:** terminar a mensagem com o trailer `Claude-Session: ...` (ver passo 4).

---

## Related Resources

- **Review completo (evidência por requisito):** `docs/review/2026-06-29-review-completo-spec.md`
- **SPEC:** `docs/SPEC.md` (seção "README.md deve conter" → C)
- **ROADMAP:** `docs/ROADMAP.md` (entrega marcada; critérios 3/3)
- **Dev-log da implementação:** `docs/dev-log/2026-06-29-implementacao-skill-3-iteracoes.md`

### Comandos úteis

```bash
# ver a subseção a editar
grep -n "Apps rodando\|re-rodaram GREEN\|captured 19 endpoints" README.md
# re-rodar só a dimensão readme-content do review (opcional, p/ confirmar 85/85)
# (o script do workflow está em .../workflows/scripts/review-completo-spec-*.js)
```

---

## Open Questions

- [ ] Capturar logs **frescos** (rodar os comandos) ou colar a saída esperada já registrada acima? Recomendado: rodar e colar a saída real, para a evidência ser genuína.

---

_Handoff gerado ao fim do ciclo de review. O deliverable está 83/85; este documento fecha os 2 restantes (ambos = o mesmo drift de logs P2/P3 no README §C)._
