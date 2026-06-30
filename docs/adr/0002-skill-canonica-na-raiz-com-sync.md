---
status: accepted
---

# Cópia canônica da skill na raiz do repo, espelhada nos projetos por script de sync

## Contexto

O SPEC exige a skill dentro de cada projeto (`<projeto>/.claude/skills/refactor-arch/`)
e prevê 2-4 iterações de ajuste. Três cópias mantidas à mão divergem na certeza, e o
próprio SPEC alerta que a skill precisa ser desacoplada/copiável.

## Decisão

A **fonte da verdade** é uma única cópia em `.claude/skills/refactor-arch/` na raiz do
repo. Um script enxuto (`scripts/sync-skill.sh`) espelha essa pasta para os três
`<projeto>/.claude/skills/refactor-arch/` antes de cada teste e antes de commitar.

## Consequências

- Separa a skill-em-desenvolvimento do código-alvo; esta sessão-raiz pode invocá-la.
- Elimina drift de 3 vias: edita-se num lugar só.
- Desvia da leitura literal do SPEC ("criar a skill dentro de code-smells-project") —
  o resultado entregue é idêntico (skill presente nos 3 projetos), só a origem muda.
- As cópias nos projetos são geradas, não editadas à mão; o sync é parte do checklist
  do ROADMAP antes de cada run/commit.
- **Git:** o root `.claude/` é gitignored (`/.claude/`) — a cópia canônica é fonte de
  dev e não vai pro repo. O entregável versionado são as cópias em
  `<projeto>/.claude/skills/refactor-arch/`, que o `.gitignore` deixa rastreáveis.
