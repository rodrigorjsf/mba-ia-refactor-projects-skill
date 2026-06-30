## Agent skills

### Issue tracker

Issues live in GitHub Issues for this repo (no external PRs as triage surface). See `docs/agents/issue-tracker.md`.

### Triage labels

Default canonical labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

### Skill authoring

**Every skill in this repo — without exception — is created and revised through the
`/writing-great-skills` skill.** Applies to `refactor-arch` and any future skill. Never
hand-author a `SKILL.md` or its reference files outside that process. This governance
lives here only; do not restate it in the project docs.

## Implementation — TDD is mandatory

**Every code change in this repo, without exception, is driven through the `/tdd`
skill** (red-green-refactor): write a failing test first, make it pass, then
refactor. Non-negotiable — applies to all of `src/` and any other code here. Never
write or edit implementation code without a failing test first.

## Documentation

Postgraduate deliverable: docs are living, not write-once.

- `README.md` and `docs/ROADMAP.md` must stay in sync with the code. Update them in the **same commit** that changes behavior, scope, or run steps — never let them drift.
- Use **Mermaid diagrams** whenever they make a flow, architecture, or state clearer. Apply colors (`classDef`/`style`) and animated edges (`e1@{ animate: true }`) where the renderer supports them; colors are the baseline, animation is best-effort.

## Applied Learning

When something fails repeatedly, when User has to re-explain, or when a workaround is found for a platform/tool limitation, add a one-line bullet here. Keep each bullet under 15 words. No explanations. Only add things that will save time in future sessions.

- Agents fail silently on wrong paths. Always verify hardcoded paths.