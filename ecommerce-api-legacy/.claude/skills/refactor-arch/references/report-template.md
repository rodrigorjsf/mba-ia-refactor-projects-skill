# Template do relatório de auditoria (Fase 2)

Salvar em `reports/audit-project-<N>.md`. Achados **ordenados por severidade decrescente** (CRITICAL → HIGH → MEDIUM → LOW). Mínimo: 5 achados, ≥1 CRITICAL ou HIGH. Cada achado traz severidade, arquivo:linha, descrição, impacto e recomendação.

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-projeto>
Stack:   <linguagem + framework + banco>
Files:   <N> analyzed | ~<linhas> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <Nome do anti-pattern>
File: <arquivo>:<linha(s)>
Description: <o que é, concreto>.
Impact: <por que dói — segurança, manutenção, correção>.
Recommendation: <transformação alvo; aponte o playbook quando aplicável>.

### [HIGH] <Nome do anti-pattern>
File: <arquivo>:<linha(s)>
Description: ...
Impact: ...
Recommendation: ...

<... um bloco por achado, sempre na ordem de severidade ...>

================================
Total: <N> findings
================================

Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]
```

## Regras

- **Um achado = uma ocorrência localizada.** Se o mesmo anti-pattern aparece em 6 lugares, ou cite os 6 nas linhas ou agrupe num achado com a lista de `arquivo:linha`.
- **Severidade vem do catálogo**, não do gosto. Ver `references/anti-patterns.md` e a régua em `CONTEXT.md`.
- **APIs deprecated** entram como achados normais (severidade conforme o risco), com o equivalente moderno na recomendação.
- O bloco final de confirmação faz parte do relatório impresso na tela, mas a pausa real é da skill (Fase 2, passo 4).
