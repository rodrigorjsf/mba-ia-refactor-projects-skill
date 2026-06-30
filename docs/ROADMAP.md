# ROADMAP — Skill `refactor-arch`

Passo a passo rastreável para implementar 100% do [`docs/SPEC.md`](./SPEC.md): uma
skill que **analisa → audita → refatora** qualquer projeto para MVC, agnóstica de
stack, validada nos 3 projetos do desafio.

**Como ler:** `[ ]` pendente · `[~]` em andamento · `[x]` concluído. Cada item liga
a um requisito do SPEC. A seção [Rastreabilidade ↔ SPEC](#rastreabilidade--spec)
prova que nada do SPEC ficou de fora. Decisões fundadoras: [ADR-0001](./adr/0001-agnosticidade-entre-stacks.md)
(agnosticidade), [ADR-0002](./adr/0002-skill-canonica-na-raiz-com-sync.md) (sync),
[ADR-0003](./adr/0003-validacao-harness-como-gate-tdd.md) (validação/TDD).
Vocabulário em [CONTEXT.md](../CONTEXT.md). Idioma e disciplina de docs em
[DOCUMENTACAO.md](./DOCUMENTACAO.md).

---

## Fluxo da skill (alvo)

```mermaid
flowchart TD
    A[Fase 1 — Análise<br/>detecta stack, mapeia arquitetura] --> B[Gera harness de<br/>caracterização + baseline]
    B --> C[Fase 2 — Auditoria<br/>cruza com catálogo, gera relatório]
    C --> D{Confirmação<br/>humana?}
    D -- não --> E[Para. Nada é modificado]
    D -- sim --> F[Snapshot 'antes'<br/>tag/branch git]
    F --> G[Fase 3 — Refatoração<br/>reestrutura para MVC]
    G --> H[Re-roda harness]
    H --> I{Baseline<br/>verde?}
    I -- não --> G
    I -- sim --> J[Refatoração aceita]

    classDef gate fill:#fde68a,stroke:#b45309,color:#000
    classDef stop fill:#fecaca,stroke:#b91c1c,color:#000
    classDef done fill:#bbf7d0,stroke:#15803d,color:#000
    class D,I gate
    class E stop
    class J done
```

---

## Fase 0 — Planejamento, alinhamento & pesquisa  _(esta sessão)_

- [x] Grilling: 6 decisões fechadas (idioma, casa da skill, validação/TDD, autoria do harness, catálogo/playbook, pesquisa)
- [x] [CONTEXT.md](../CONTEXT.md) — glossário do domínio da skill
- [x] ADRs [0001](./adr/0001-agnosticidade-entre-stacks.md) · [0002](./adr/0002-skill-canonica-na-raiz-com-sync.md) · [0003](./adr/0003-validacao-harness-como-gate-tdd.md)
- [x] Este ROADMAP
- [x] Esqueleto do [README.md](../README.md)
- [x] [DOCUMENTACAO.md](./DOCUMENTACAO.md) + template de dev-log
- [x] `.claude/rules/` via `/create-rule` — `refactor-arch-skill.md` + `audit-reports.md`
- [x] Workflow de pesquisa web → [`docs/research/2026-06-29-digest-pesquisa.md`](./research/2026-06-29-digest-pesquisa.md)
- [x] `.gitignore` ancorado em `/.claude/` (root): a skill canônica + rules da raiz ficam **fora** do git (fonte de dev), e as **cópias nos 3 projetos** (`<projeto>/.claude/skills/refactor-arch/`) ficam **rastreáveis/commitáveis**, como exige o SPEC.

> **Saída desta fase:** docs de planejamento. **Nada** da skill é implementado aqui.

---

## Fase 1 — Análise manual dos 3 projetos  _(SPEC §1)_

Entender os problemas antes de codar a detecção. Documentar na seção **Análise
Manual** do README. Mínimo por projeto: **≥5 problemas**, sendo **≥1 CRITICAL/HIGH,
≥2 MEDIUM, ≥2 LOW**.

- [ ] **code-smells-project** (Python/Flask, e-commerce) — ≥5 problemas classificados e justificados
- [ ] **ecommerce-api-legacy** (Node/Express, LMS+checkout) — ≥5 problemas classificados e justificados
- [ ] **task-manager-api** (Python/Flask, parcialmente organizado) — ≥5 problemas classificados e justificados

> **Insumo pronto:** [`docs/research/findings-baseline.md`](./research/findings-baseline.md)
> já traz achados localizados (arquivo:linha) por projeto, descobertos no
> planejamento. A Fase 1 confirma, expande e completa (Projeto 3 foi lido só
> parcialmente).

---

## Fase 2 — Construção da skill  _(SPEC §2)_

Cópia canônica em `.claude/skills/refactor-arch/` na raiz ([ADR-0002](./adr/0002-skill-canonica-na-raiz-com-sync.md)).

### 2.1 — Estrutura

- [ ] `SKILL.md` com as **3 fases sequenciais** (Análise → Auditoria → Refatoração) e nome `refactor-arch` (obrigatório, não alterar)
- [ ] Reference files cobrindo as **5 áreas de conhecimento obrigatórias** (tabela abaixo)
- [ ] `scripts/sync-skill.sh` espelhando a skill nos 3 projetos

| Área de conhecimento | Reference file (sugerido) | Cobre |
|---|---|---|
| Análise de projeto | `references/analysis.md` | heurísticas de detecção de linguagem/framework/banco e mapeamento de arquitetura |
| Catálogo de anti-patterns | `references/anti-patterns.md` | anti-patterns com sinais de detecção + severidade |
| Template de relatório | `references/report-template.md` | formato padronizado do relatório (Fase 2) |
| Guidelines de arquitetura | `references/mvc-guidelines.md` | regras do MVC alvo (responsabilidades de cada camada) |
| Playbook de refatoração | `references/playbook.md` | transformações antes/depois por anti-pattern |

### 2.2 — Catálogo (`anti-patterns.md`) — alvo ~12-15

- [ ] ≥8 anti-patterns com **severidade distribuída** (CRITICAL/HIGH/MEDIUM/LOW)
- [ ] Inclui **detecção de APIs deprecated** (seção dedicada; ex: `datetime.utcnow()` → `datetime.now(timezone.utc)`)
- [ ] Cada anti-pattern com sinais de detecção **acionáveis** (heurística regex/AST, não "código ruim")
- [ ] Semeado do `patterns.py` do plugin `security-guidance` (fonte local) + OWASP API Top 10 (digest de pesquisa)

### 2.3 — Playbook (`playbook.md`) — alvo ~8-10

- [ ] ≥8 transformações com **exemplos de código antes/depois**
- [ ] Cobre os de maior impacto: SQLi→parametrizado, God Class→MVC, segredo→config/env, senha→hash, callback hell→async/await, N+1→join/batch, lógica-no-controller→service, debug→env-gated
- [ ] Exemplos **por stack** (Flask/SQLite e Express/SQLite), conforme [ADR-0001](./adr/0001-agnosticidade-entre-stacks.md)

### 2.4 — Comportamento obrigatório da skill

- [ ] **Fase 2 pausa e pede confirmação** antes de modificar qualquer arquivo
- [ ] **Fase 3 gera o harness** na Fase 1 e o re-roda para validar (boot + endpoints) — [ADR-0003](./adr/0003-validacao-harness-como-gate-tdd.md)
- [ ] Skill **agnóstica**: nada hardcoded para um projeto específico — [ADR-0001](./adr/0001-agnosticidade-entre-stacks.md)

### 2.5 — Aprofundamento (deep-research)

- [ ] Rodar deep-research sobre os achados e **gaps** que a pesquisa enxuta não cobriu, refinando catálogo/playbook antes de fechar a skill

---

## Fase 3 — Execução nos 3 projetos  _(SPEC §3)_

Para **cada** projeto: sync da skill → snapshot "antes" → rodar `/refactor-arch` →
salvar relatório → commitar. O snapshot "antes" preserva o estado para o comparativo
do README (seção C) — a Fase 3 sobrescreve a estrutura.

> **Security tooling:** o plugin `security-guidance` (passivo) é a rede de segurança
> automática — revisa nossos diffs e o commit da refatoração, garantindo que a Fase 3
> não introduz vulnerabilidade nova. A auditoria do código legado é da própria skill
> (Fase 2); o `patterns.py` do plugin semeia o catálogo (2.2). SAST ativo sobre o
> legado (plugin `security-scanning`) ficou **fora de escopo** por decisão de projeto.

### Projeto 1 — code-smells-project (Python/Flask)

- [ ] `sync-skill.sh` copiou a skill para o projeto
- [ ] Snapshot "antes" (tag/branch git + captura da estrutura de diretórios)
- [ ] Fase 1 detecta stack e imprime resumo
- [ ] Fase 2 encontra **≥5** dos problemas da análise manual
- [ ] Confirmação dada; Fase 3 executada
- [ ] Relatório salvo em `reports/audit-project-1.md`
- [ ] Código refatorado commitado
- [ ] **Checklist de Validação** preenchido (abaixo)

### Projeto 2 — ecommerce-api-legacy (Node/Express)

- [ ] `.claude/skills/refactor-arch/` copiada para o projeto
- [ ] Snapshot "antes"
- [ ] 3 fases executam corretamente nesta stack diferente
- [ ] Relatório salvo em `reports/audit-project-2.md`
- [ ] Código refatorado commitado
- [ ] **Checklist de Validação** preenchido

### Projeto 3 — task-manager-api (Python/Flask, parcialmente organizado)

- [ ] `.claude/skills/refactor-arch/` copiada para o projeto
- [ ] Snapshot "antes"
- [ ] Fase 1 detecta Python/Flask e identifica o domínio Task Manager
- [ ] Fase 2 identifica problemas mesmo num projeto parcialmente organizado
- [ ] Fase 3 melhora a estrutura **sem quebrar** a aplicação
- [ ] Relatório salvo em `reports/audit-project-3.md`
- [ ] Código refatorado commitado
- [ ] **Checklist de Validação** preenchido

### Checklist de Validação  _(verbatim do SPEC — replicar por projeto)_

```markdown
### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

---

## Fase 4 — Documentação final & entrega

- [ ] README seção **A) Análise Manual** (Fase 1)
- [ ] README seção **B) Construção da Skill** (decisões de design, anti-patterns, agnosticidade, desafios)
- [ ] README seção **C) Resultados** (resumo dos relatórios, antes/depois, checklist preenchido ×3, logs/screenshots das apps rodando)
- [ ] README seção **D) Como Executar** (pré-requisitos, comandos por projeto, como validar)
- [ ] Dev-log atualizado a cada iteração ([DOCUMENTACAO.md](./DOCUMENTACAO.md))
- [ ] README + ROADMAP em sync no **mesmo commit** de cada mudança de comportamento
- [ ] **Publicação:** push + repositório **público** no GitHub (fork), com todos os entregáveis

---

## Critérios de Aceite  _(gate final — verbatim do SPEC)_

Mínimos em **todos os 3 projetos**:

| Critério | Requisito | P1 | P2 | P3 |
|---|---|:--:|:--:|:--:|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO | [ ] | [ ] | [ ] |
| Fase 2 encontra ≥ 5 findings | OBRIGATÓRIO | [ ] | [ ] | [ ] |
| Fase 2 inclui ≥ 1 CRITICAL ou HIGH | OBRIGATÓRIO | [ ] | [ ] | [ ] |
| Fase 3 app funciona após refatoração | OBRIGATÓRIO | [ ] | [ ] | [ ] |

---

## Entregáveis  _(SPEC §Entregável)_

- [ ] Skill completa em `.claude/skills/refactor-arch/` **dentro dos 3 projetos**
- [ ] Código refatorado dos 3 projetos commitado
- [ ] `reports/audit-project-{1,2,3}.md` (3 relatórios)
- [ ] `README.md` atualizado (seções A/B/C/D)
- [ ] Repositório **público** no GitHub (fork) com tudo acima

---

## Rastreabilidade ↔ SPEC

| Requisito do SPEC | Onde é honrado |
|---|---|
| Skill analisa/audita/refatora para MVC, agnóstica | Fases 2-3 · [ADR-0001](./adr/0001-agnosticidade-entre-stacks.md) |
| Severidades CRITICAL/HIGH/MEDIUM/LOW | [CONTEXT.md](../CONTEXT.md) · catálogo (2.2) |
| Análise manual ≥5 problemas/projeto (1 CRIT/HIGH, 2 MED, 2 LOW) | Fase 1 · README A |
| SKILL.md com 3 fases sequenciais | 2.1 |
| 5 áreas de conhecimento em reference files | 2.1 (tabela) |
| Catálogo ≥8, severidade distribuída | 2.2 |
| Catálogo detecta APIs deprecated | 2.2 |
| Playbook ≥8 antes/depois | 2.3 |
| Fase 2 pausa para confirmação | 2.4 |
| Fase 3 valida (boot + endpoints) | 2.4 · [ADR-0003](./adr/0003-validacao-harness-como-gate-tdd.md) |
| Execução + relatório + commit nos 3 projetos | Fase 3 |
| Checklist de Validação por projeto | Fase 3 |
| Critérios de Aceite 3/3 | Gate final |
| README A/B/C/D | Fase 4 |
