# Diretriz de Documentação

Como a documentação deste projeto é produzida e mantida em sync ao longo das
iterações da skill. Documentação é **viva**, não write-once.

## Idioma

Decisão do projeto: **todos os artefatos do projeto em pt-BR** — README, relatórios
de auditoria, `SKILL.md` + reference files, ADRs, `.claude/rules/`, `CONTEXT.md`,
ROADMAP, dev-log e comentários de código. (Único arquivo meta que permanece em inglês:
o `CLAUDE.md` de governança, pré-existente, não retraduzido.)

## Mapa dos artefatos

| Artefato | Papel | Quando muda |
|---|---|---|
| [`README.md`](../README.md) | Vitrine + entregável avaliado (seções A/B/C/D) | a cada mudança de comportamento/escopo/execução |
| [`docs/ROADMAP.md`](./ROADMAP.md) | Tracker com checkboxes do SPEC | ao concluir/iniciar um passo |
| [`CONTEXT.md`](../CONTEXT.md) | Glossário do domínio da skill | quando um termo é resolvido |
| [`docs/adr/`](./adr/) | Decisões difíceis de reverter | quando uma decisão arquitetural é tomada |
| [`docs/dev-log/`](./dev-log/) | Diário de evolução por iteração | a cada iteração/run da skill |
| `reports/audit-project-{1,2,3}.md` | Saída da Fase 2 (entregável SPEC) | a cada run de auditoria |
| [`docs/research/`](./research/) | Digests de pesquisa que embasam catálogo/playbook | quando uma pesquisa é feita |

## Dev-log — relatório de melhoria por iteração

O SPEC prevê 2-4 iterações de ajuste da skill. **Cada iteração** ganha um arquivo
datado em `docs/dev-log/` seguindo [`_TEMPLATE.md`](./dev-log/_TEMPLATE.md):
`AAAA-MM-DD-<slug>.md` (ex: `2026-07-02-catalogo-deprecated.md`).

Registra: o que mudou na skill, por quê, quais achados/gaps motivaram, o resultado da
validação (harness verde/vermelho) e o que ficou pendente. É a memória do processo —
de onde a seção **B) Construção da Skill** e o **C) Desafios** do README são puxados.

## Disciplina de sync

- **Mesmo commit.** Qualquer mudança de comportamento, escopo ou passo de execução
  atualiza `README.md` **e** `docs/ROADMAP.md` no **mesmo commit** que muda o código.
  Nunca deixar derivar. (Reforço path-scoped em `.claude/rules/`.)
- **Checkbox segue a realidade.** Um item do ROADMAP só vira `[x]` com evidência
  (harness verde, relatório salvo, commit feito) — não por intenção.
- **ADR ao decidir, não depois.** Decisão difícil de reverter + surpreendente + com
  trade-off real → ADR na hora.

## Mermaid

Usar diagramas **Mermaid** sempre que clarearem um fluxo, arquitetura ou estado
(ex: as 3 fases da skill, antes/depois da estrutura). Cores (`classDef`/`style`) são
o baseline; edges animadas (`e1@{ animate: true }`) são best-effort onde o renderer
suporta.
