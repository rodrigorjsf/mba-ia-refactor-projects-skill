# Relatório de Conformidade — Skill `refactor-arch` (MBA IA)

**Data:** 2026-06-29
**Revisor-chefe:** Lead Reviewer (síntese de 8 dimensões + 3 verificadores adversariais independentes)
**Documento base:** `docs/SPEC.md` — *Skill de Auditoria e Refatoração Arquitetural*
**Repositório:** rodrigorjsf/mba-ia-refactor-projects-skill (fork público de devfullcycle)

---

## 1. Veredicto Geral

**GAPS_ENCONTRADOS**

Todos os quatro critérios de aceite obrigatórios do SPEC foram atingidos em 3/3 projetos, e a totalidade da execução (boots + harness) foi confirmada adversarialmente de forma independente. No entanto, um requisito explícito da seção "README.md deve conter" (SPEC l.374) não está plenamente atendido: a subseção C) exige "Screenshots ou logs mostrando **as aplicações** rodando após refatoração" — plural, todos os 3 projetos. Apenas P1 apresenta um bloco de log real no README (ll.270-278); P2 e P3 são cobertos por uma frase em prosa na linha 279-281 ("re-rodaram GREEN da mesma forma") sem nenhum bloco de código ou screenshot.

O SPEC usa "deve conter" como formulação mandatória. A ausência do log real para P2 e P3 no README configura um requisito não atendido. A execução funcional dos três projetos foi confirmada adversarialmente (EXIT=0, harness GREEN), mas isso não supre a exigência documental. O entregável principal (skill + refatoração dos 3 projetos) é sólido; o gap é isolado ao conteúdo documental do README.

---

## 2. Critérios de Aceite Obrigatórios (tabela do SPEC, seção "Critérios de Aceite")

> O SPEC define: "A skill deve atingir os seguintes mínimos em **todos os 3 projetos**"

| Critério | P1 code-smells-project | P2 ecommerce-api-legacy | P3 task-manager-api | Resultado |
|---|---|---|---|---|
| Fase 1 detecta stack corretamente | ✅ Python 3.14 + Flask 3.1.1 + SQLite | ✅ Node.js + Express 4.18 + SQLite | ✅ Python 3 + Flask 3.0.0 + SQLAlchemy | **3/3 PASS** |
| Fase 2 >= 5 findings | ✅ 17 findings | ✅ 15 findings | ✅ 13 findings | **3/3 PASS** |
| Fase 2 >= 1 CRITICAL ou HIGH | ✅ 5 CRITICAL + 4 HIGH | ✅ 4 CRITICAL + 4 HIGH | ✅ 3 CRITICAL + 2 HIGH | **3/3 PASS** |
| Fase 3 aplicação funciona após refatoração | ✅ Harness GREEN, exit 0, 19 endpoints | ✅ Harness GREEN, exit 0, 3 endpoints | ✅ Harness GREEN, exit 0, 22 endpoints | **3/3 PASS** |

**Todos os 4 critérios obrigatórios do SPEC aprovados em 3/3 projetos.**

---

## 3. Mapeamento Completo de Requisitos do SPEC

### 3.1 Estrutura da Skill

| Requisito do SPEC | Evidência | Veredicto |
|---|---|---|
| SKILL.md existe e o nome da skill é exatamente `refactor-arch` | Frontmatter linha 2: `name: refactor-arch` (exato) nos 3 projetos | ✅ |
| Arquivo SKILL.md presente | 60 linhas, abaixo do limite de 500; presente em 3 paths | ✅ |
| SKILL.md define 3 fases sequenciais: Análise → Auditoria → Refatoração | SKILL.md l.8: declarado; Fase 1 l.23, Fase 2 l.37, Fase 3 l.46 | ✅ |
| Reference files cobrem as 5 áreas obrigatórias em Markdown | `analysis.md`, `anti-patterns.md`, `report-template.md`, `mvc-guidelines.md`, `playbook.md` todos presentes e verificados | ✅ |
| Área 1 — Análise de projeto | `analysis.md`: heurísticas de detecção de linguagem, framework, banco, arquitetura (ll.5-53) | ✅ |
| Área 2 — Catálogo de anti-patterns | `anti-patterns.md`: 19 anti-patterns + seção de APIs deprecated (ll.16-159) | ✅ |
| Área 3 — Template de relatório | `report-template.md`: formato padronizado com regras (ll.1-44) | ✅ |
| Área 4 — Guidelines de arquitetura MVC | `mvc-guidelines.md`: responsabilidades de todas as camadas (ll.1-70) | ✅ |
| Área 5 — Playbook de refatoração | `playbook.md`: 11 padrões com exemplos antes/depois (ll.7-216) | ✅ |
| Skill presente em CADA um dos 3 projetos (`<projeto>/.claude/skills/refactor-arch/`) | `find` confirma 3 paths; `md5sum SKILL.md` idêntico nos 3: `2275e6f70c213aa860693cb4dfc13985` | ✅ |
| Reference files idênticos nos 3 projetos | md5sum de todos os 5 reference files: idênticos em code-smells, ecommerce-api-legacy, task-manager-api | ✅ |

### 3.2 Catálogo de Anti-patterns e Playbook (mínimos do SPEC)

| Requisito do SPEC | Evidência | Veredicto |
|---|---|---|
| Catálogo >= 8 anti-patterns | 19 anti-patterns (mínimo de 8 amplamente superado) | ✅ |
| Severidade distribuída entre CRITICAL/HIGH/MEDIUM/LOW | CRITICAL=5, HIGH=5, MEDIUM=5, LOW=4 — todos os 4 níveis presentes | ✅ |
| Catálogo inclui detecção de APIs deprecated com equivalente moderno | `anti-patterns.md` l.146: seção dedicada "APIs deprecated (detecção obrigatória)" com tabela de 6 entradas mapeando deprecated → moderno | ✅ |
| Cada anti-pattern tem sinais de detecção acionáveis | Todos os 19 têm sinais de código concretos (ex: `cursor.execute("..." + var)`, `senha == row["senha"]`) — nenhum usa descrição genérica | ✅ |
| Playbook >= 8 transformações com exemplos ANTES/DEPOIS | 11 transformações (## 1 a ## 11); 42 ocorrências de marcadores `# Antes / # Depois / // Antes / // Depois` | ✅ |
| Catálogo e playbook cobrem Flask E Express (dual-stack, não hardcoded a um projeto) | Todos os 19 anti-patterns têm seções `**Flask/Python:**` E `**Express/Node:**`; playbook: cabeçalho l.3 afirma agnosticidade explicitamente | ✅ |

### 3.3 Gate de Confirmação da Fase 2 (obrigatório pelo SPEC)

> SPEC l.177: "A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo"

| Requisito do SPEC | Evidência | Veredicto |
|---|---|---|
| SKILL.md instrui PARAR e pedir confirmação [s/n] antes de tocar arquivos-fonte | SKILL.md l.42: texto exato do prompt; l.10: "Nunca pule a confirmação. A Fase 2 termina pedindo autorização humana; só a Fase 3 toca arquivos-fonte." | ✅ |
| Relatório P1 exibe prompt de confirmação | `reports/audit-project-1.md` l.126: "Fase 2 concluida. Prosseguir com a refatoracao (Fase 3)? [s/n]" | ✅ |
| Relatório P2 exibe prompt de confirmação | `reports/audit-project-2.md` l.107: texto idêntico ao prescrito | ✅ |
| Relatório P3 exibe prompt de confirmação | `reports/audit-project-3.md` l.95: texto idêntico ao prescrito | ✅ |

### 3.4 Execução P1 — code-smells-project (Python/Flask)

| Requisito do SPEC | Evidência | Veredicto |
|---|---|---|
| Fase 1 detecta stack (Python/Flask/SQLite) e domínio e-commerce | Report header l.6-9: "Python 3.14 + Flask 3.1.1 + SQLite"; domínio produtos/usuários/pedidos | ✅ |
| Fase 2 >= 5 achados com >= 1 CRITICAL/HIGH | 17 findings: CRITICAL=5, HIGH=4, MEDIUM=4, LOW=4 | ✅ |
| Findings ordenados por severidade (CRITICAL → LOW) | Ordem estrita no relatório: 5 CRITICAL → 4 HIGH → 4 MEDIUM → 4 LOW | ✅ |
| Cada finding com arquivo:linha exatos | Todos os 17 têm linha `File:` com referências numéricas exatas (ex: `app.py:7`, `models.py:28, 47-50`) | ✅ |
| Relatório segue o template definido | Correspondência exata com `report-template.md`: banner `====`, ARCHITECTURE AUDIT REPORT, seções Summary/Findings, prompt de confirmação | ✅ |
| Relatório inclui detecção de APIs deprecated | Nota de deprecated-API presente no relatório (template-template.md l.43) | ✅ |
| Fase 3 estrutura MVC: config, models, views/rotas, controllers, error centralizado, entry point | `config/settings.py`, `models/`, `views/routes.py`, `controllers/` (6 files), `middlewares/error_handler.py`, `app.py` (composition root com `create_app()`) | ✅ |
| Config sem segredo hardcoded | `config/settings.py` ll.11-21: todos os valores via `os.environ.get`; `grep 'minha-chave-super-secreta'` → zero resultados | ✅ |
| SQL concatenado eliminado | `grep "execute(..."` → zero concatenações; todos os queries parametrizados com `?` | ✅ |
| Senha em claro eliminada | `generate_password_hash`/`check_password_hash` via werkzeug em `models/usuario_model.py:41,52` e `database/connection.py:119` | ✅ |
| App inicia sem erro (boot real) | Harness `characterize.py` em venv isolado: cold boot, 19 endpoints capturados, exit 0 | ✅ |
| Harness de caracterização GREEN | "GREEN — every endpoint preserved its status class." Exit 0 | ✅ |
| Relatório salvo em `reports/audit-project-1.md` | Arquivo existe (12.850 bytes); `git ls-files` confirma rastreamento | ✅ |
| Código refatorado commitado | Commit `80b16ac` "feat(code-smells-project): refatora para MVC via refactor-arch (P1)"; 24 arquivos `.py` rastreados; `git status` limpo | ✅ |
| TODOS os endpoints originais respondem | ⚠️ 17/19 preservados com status class idêntico. 2 admin endpoints: `/admin/query` 200→404 (endpoint REMOVIDO — eliminação do CRITICAL arbitrary-SQL, mandatado por CONTEXT.md l.64-67); `/admin/reset-db` 200→401 (hardening de auth, still responds). Baseline re-baselined com documentação transparente no relatório. | ⚠️ |

> **Nota sobre `/admin/query`:** O SPEC (l.14) exige "eliminando os problemas encontrados" na Fase 3. O endpoint `/admin/query` era ele mesmo o achado CRITICAL de execução arbitrária de SQL. Mantê-lo respondendo 200 violaria diretamente o requisito de eliminação de achados. A remoção é mandatada pelo próprio SPEC; o desvio é documentado e re-baselined de forma transparente. Não configura gap funcional.

### 3.5 Execução P2 — ecommerce-api-legacy (Node.js/Express)

| Requisito do SPEC | Evidência | Veredicto |
|---|---|---|
| Skill copiada para `ecommerce-api-legacy/` | SKILL.md (6.978 bytes) + 5 reference files confirmados por `ls`; md5sum idêntico ao P1 | ✅ |
| Fase 1 detecta stack Node/Express + domínio LMS/checkout | Report l.5: "Node.js + Express 4.18 + SQLite"; domínio courses/enrollments/checkout/financial-report | ✅ |
| Fase 2 >= 5 achados com >= 1 CRITICAL/HIGH | 15 findings: CRITICAL=4, HIGH=4, MEDIUM=4, LOW=3; 8 CRITICAL/HIGH | ✅ |
| Achados ordenados por severidade | 4×CRITICAL → 4×HIGH → 4×MEDIUM → 3×LOW | ✅ |
| Cada achado com arquivo:linha exatos | 15/15 findings com `File: <arquivo>:<linha(s)>` | ✅ |
| Fase 3 estrutura MVC sob `src/` | `src/models/` (6), `src/controllers/` (3), `src/routes/index.js`, `src/services/` (2), `src/config/index.js`, `src/middlewares/` (auth, error) | ✅ |
| Config sem hardcoded | `src/config/index.js` lê de `process.env` com defaults dev-only marcados; `grep senha_super_secreta / pk_live_` → NONE | ✅ |
| Weak hash eliminado | `password.service.js`: `crypto.scryptSync` salted; `grep badCrypto/md5/toString('base64')` → apenas 1 comentário, zero uso real | ✅ |
| Log de cartão eliminado | `payment.service.js`: log apenas `pan=****4444`; gateway key nunca logada | ✅ |
| SQL concatenado eliminado | Grep SQL verbs + `${` / string-concat → "NO CONCAT FOUND"; todos os models usam `?` parameter placeholders | ✅ |
| App inicia e endpoints respondem (boot real + harness GREEN) | `node harness/run.js verify` → "RESULT: GREEN", EXIT_CODE=0; 3 endpoints originais (POST /api/checkout, GET /api/admin/financial-report, DELETE /api/users/:id) todos presentes em `src/routes/index.js:11-16` | ✅ |
| Relatório em `reports/audit-project-2.md` | Arquivo existe (9.608 bytes); commitado em `cc1fea7` | ✅ |
| Código refatorado commitado | Commit `cc1fea7` "feat(ecommerce-api-legacy): refatora para MVC via refactor-arch (P2, Node/Express)"; `git status` limpo | ✅ |

### 3.6 Execução P3 — task-manager-api (Flask parcial)

| Requisito do SPEC | Evidência | Veredicto |
|---|---|---|
| Skill copiada para `task-manager-api/` | `ls` confirma SKILL.md + 5 reference files em `task-manager-api/.claude/skills/refactor-arch/` | ✅ |
| Fase 1 detecta Python/Flask e domínio Task Manager | Report l.5: "Python 3 + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1 (SQLite, sqlite:///tasks.db)"; domínio tasks/users/categories/reports | ✅ |
| Fase 2 identifica problemas mesmo em projeto parcialmente organizado | 13 findings (3C+2H+4M+4L); inclui achados de segurança (md5, hardcoded SECRET_KEY, to_dict vazando password) + problemas arquiteturais | ✅ |
| Fase 2 >= 5 achados com >= 1 CRITICAL/HIGH | 13 findings; 5 CRITICAL/HIGH | ✅ |
| Findings ordenados por severidade | 3×CRITICAL → 2×HIGH → 4×MEDIUM → 4×LOW (ordem estrita) | ✅ |
| Cada finding com arquivo:linha exatos | Todos os 13 findings com `File:` e linha(s) numéricas exatas | ✅ |
| Inclui achado de API deprecated com equivalente moderno | `reports/audit-project-3.md` ll.85-89: "[LOW] APIs deprecated de datetime ... `datetime.utcnow()` ... Recommendation: `datetime.now(datetime.timezone.utc)`". Segundo achado deprecated (hashlib.md5 para senha) classificado CRITICAL | ✅ |
| Fase 3 melhora estrutura SEM quebrar a aplicação | `config/`, `controllers/` (5), `models/`, `routes/`, `middlewares/`, `services/` adicionados/corrigidos; harness GREEN 22/22 endpoints | ✅ |
| App inicia e TODOS endpoints respondem | `harness/characterize.py --compare harness/baseline.json`: "RESULT: GREEN", EXIT=0; 22 endpoints 2xx; app.url_map tem exatamente 22 rotas = 22 harness ROUTES = 22 decoradores `@route` do commit original 6d1ce62 (bijeção verificada) | ✅ |
| md5 eliminado | `grep -rni 'md5\|base64\|hexdigest' --include=*.py` → apenas 1 comentário; `set_password` usa `generate_password_hash` (`models/user.py:38`) | ✅ |
| SECRET_KEY hardcoded eliminado | `config/settings.py:17`: `SECRET_KEY = os.environ.get('SECRET_KEY','dev-only...')`; `grep 'super-secret-key-123'` → 0 hits | ✅ |
| `to_dict` não vaza password | `User.to_dict()` (`models/user.py:25-34`) omite campo password; harness COMPARE confirma: "removed top keys [password]" vs baseline | ✅ |
| Relatório em `reports/audit-project-3.md` | Arquivo existe (7.982 bytes); rastreado em `git ls-files` em root e em `task-manager-api/reports/` | ✅ |
| Código refatorado commitado | Commit `d91f929` "feat(task-manager-api): refatora para MVC via refactor-arch (P3, Flask parcial)"; `git status --porcelain` vazio | ✅ |

### 3.7 Entregáveis e Estado do Repositório

| Requisito do SPEC | Evidência | Veredicto |
|---|---|---|
| Repositório público no GitHub | `gh repo view --json`: `{"isFork":true, "visibility":"PUBLIC", "parent":{"owner":"devfullcycle","name":"mba-ia-refactor-projects-skill"}}` | ✅ |
| Fork do repositório base (devfullcycle/mba-ia-refactor-projects-skill) | Confirmado: `nameWithOwner: rodrigorjsf/mba-ia-refactor-projects-skill`, parent: devfullcycle | ✅ |
| Skill em `.claude/skills/refactor-arch/` nos 3 projetos | `find` e `git ls-files`: 6 arquivos rastreados por projeto (SKILL.md + 5 references) | ✅ |
| Código refatorado dos 3 projetos commitado | Commits `80b16ac` (P1), `cc1fea7` (P2), `d91f929` (P3) com estrutura MVC completa | ✅ |
| `reports/audit-project-1.md` na raiz | Existe (12.850 bytes), rastreado por `git ls-files` | ✅ |
| `reports/audit-project-2.md` na raiz | Existe (9.608 bytes), rastreado por `git ls-files` | ✅ |
| `reports/audit-project-3.md` na raiz | Existe (7.982 bytes), rastreado por `git ls-files` | ✅ |
| Tudo pushado (local == remote) | `git rev-parse main == origin/main`: `76c24f88cd45832554b004ec3cfb5985338eaf61`; `git rev-list --count main...origin/main = 0\t0` | ✅ |

### 3.8 Conteúdo do README (seções A/B/C/D)

| Requisito do SPEC | Evidência | Veredicto |
|---|---|---|
| **A) Análise Manual** — lista de problemas por projeto (>= 5 por projeto) | README ll.67-119: três tabelas, P1=14 linhas, P2=13 linhas, P3=12 linhas; todos superam mínimo de 5 | ✅ |
| **A)** Classificação por severidade CRITICAL/HIGH/MEDIUM/LOW | Coluna "Severidade" em todas as tabelas; P1: 5C+4H+4M+1L, P2: 4C+4H+4M+3L, P3: 3C+2H+4M+4L | ✅ |
| **A)** Justificativa de por que cada problema é relevante | Coluna "Por que importa" com justificativas técnicas específicas (ex: "Input direto na query → injeção total, bypass de login") | ✅ |
| **B) Construção da Skill** — decisões de design (SKILL.md e reference files) | README ll.124-142: tabela das 5 áreas + princípios de design (leading words, progressive disclosure, régua de severidade inline) | ✅ |
| **B)** Anti-patterns incluídos e por quê | README ll.144-151: "19 entradas ... semeado a partir dos problemas reais dos 3 projetos e do OWASP API Top 10"; dual-stack documentado | ✅ |
| **B)** Como garantiu agnosticidade de tecnologia | README ll.153-158: skill única copiada 3×; Fase 1 detecta stack; catálogo dual-stack; harness opera em HTTP; ADR-0001 referenciado | ✅ |
| **B)** Desafios encontrados e como resolveu | README ll.169-197: diagrama Mermaid v1→v2→v3 com gaps concretos documentados (régua de severidade, gate de status-class, crypto.scrypt, boot via subprocess) | ✅ |
| **C) Resultados** — resumo de findings por severidade dos 3 projetos | README ll.204-208: tabela P1=5\|4\|4\|4\|17, P2=4\|4\|4\|3\|15, P3=3\|2\|4\|4\|13 | ✅ |
| **C)** Comparativo ANTES/DEPOIS da estrutura por projeto | README ll.215-244: três blocos ASCII de antes/depois por projeto | ✅ |
| **C)** Checklist de validação preenchido x3 | README ll.248-265: tabela com todos os itens do SPEC checklist, todos marcados ✅ para P1, P2, P3 | ✅ |
| **C)** Screenshots ou logs mostrando as aplicações rodando após refatoração | P1: bloco de código real com "captured 19 endpoints" e "GREEN — every endpoint preserved its status class." README ll.269-281. P2 e P3: apenas afirmação em prosa ("re-rodaram GREEN da mesma forma") — sem bloco de log ou screenshot real | ❌ |
| **C)** Observações sobre como a skill se comportou em stacks diferentes | README ll.283-293: bullets por stack (Flask monolith, Node/Express, Flask parcialmente organizado) com observações técnicas específicas | ✅ |
| **D) Como Executar** — pré-requisitos | README ll.299-302: Claude Code + Python 3.12+ + Node.js 18+ | ✅ |
| **D)** Comandos para executar a skill em cada projeto | README ll.308-311: três comandos `cd <projeto> && claude "/refactor-arch"` | ✅ |
| **D)** Como validar que a refatoração funcionou | README ll.317-338: comandos de harness distintos por projeto, `# espera: GREEN` anotado; instruções de `python app.py` / `node src/app.js` com variáveis de ambiente | ✅ |

---

## 4. Resultados da Verificação Adversarial (boots e harness reais)

Três verificadores independentes executaram boots reais e harnesses dos projetos refatorados. Nenhuma afirmação dos revisores de dimensão foi refutada.

### P1 — code-smells-project

**Veredicto adversarial:** CONFIRMED

Comandos executados independentemente:
- `./venv/bin/python -c "import requests, flask, flask_cors"` → deps ok
- `./venv/bin/python harness/characterize.py --out <scratch>/myrun.json --baseline harness/baseline.json` → "captured 19 endpoints", "GREEN — every endpoint preserved its status class.", EXIT=0
- `grep -rn "minha-chave-super-secreta" --include='*.py'` → zero resultados
- `grep -rn "execute(" models/ database/` → todos parametrizados com `?`
- `grep -rn "md5|sha1|base64|generate_password_hash|check_password_hash"` → apenas werkzeug hashing em `usuario_model.py` + `connection.py`
- Inspeção direta de `harness/myrun.json`: `/admin/query=404`, `/admin/reset-db=401`

Nenhuma afirmação refutada.

### P2 — ecommerce-api-legacy

**Veredicto adversarial:** CONFIRMED

Comandos executados independentemente:
- `node harness/run.js verify` → "RESULT: GREEN", EXIT_CODE=0 para os 3 endpoints (POST /api/checkout 2xx(200), GET /api/admin/financial-report 2xx(200), DELETE /api/users/:id 4xx(401))
- `PORT=3055 node src/app.js` → "[info] LMS API rodando na porta 3055..."
- `curl` direto: checkout 200 `{"msg":"Sucesso","enrollment_id":2}`, financial-report 200 com shape `[{course,revenue,students:[{student,paid}]}]`, DELETE sem auth 401, DELETE com `Authorization: Bearer <ADMIN_TOKEN>` correto → 200 "Usuário deletado (matrículas e pagamentos removidos em transação)"
- `grep -rn "senha_super_secreta|pk_live_|secreta_prod"` → NONE
- `grep -rni "badCrypto|md5|toString('base64')"` → apenas um comentário; hashing real: `crypto.scryptSync` salted
- `grep` SQL com `${` ou string-concat → "NO CONCAT FOUND"
- Verificação de `src/db/seed.js`: `passwordService.hash('123')` (scrypt), não plaintext
- Verificação de `payment.service.js`: log apenas `pan=****4444`

Nenhuma afirmação refutada. Observação menor não-refutante: `checkout.controller.js:34` usa `password || '123456'` como fallback antes do hash (fraqueza de default não documentada no relatório, não está na categoria "must be gone").

### P3 — task-manager-api

**Veredicto adversarial:** CONFIRMED

Comandos executados independentemente:
- `rm -f instance/tasks.db tasks.db; PYTHONPATH=<proj> .venv/bin/python harness/characterize.py <scratch>/myrun.json --compare harness/baseline.json` → "RESULT: GREEN", EXIT_CODE=0, 22/22 endpoints 2xx
- `grep -rn 'super-secret-key-123|taskmanager@gmail.com|senha123' --include=*.py` → 0 hits
- `grep -rni 'md5|base64|hexdigest' --include=*.py` → 1 comentário apenas
- `grep password` em models/, routes/, controllers/, services/ → sem vazamento
- `cat config/settings.py` → `SECRET_KEY = os.environ.get(...)` confirmado
- POST /login + GET /users/1 em live client → campo `password` ausente do JSON de resposta

Nenhuma afirmação refutada.

---

## 5. Gaps Encontrados

### Gap 1 — README C): ausência de logs/screenshots para P2 e P3

**Tipo:** Documental
**Requisito do SPEC:** "Screenshots ou logs mostrando as aplicações rodando após refatoração" (seção README.md deve conter, item C)
**Evidência do gap:** README ll.269-281: apenas P1 exibe bloco de código real com output do harness ("captured 19 endpoints → harness/post.json", "GREEN — every endpoint preserved its status class."). P2 e P3 são cobertos por uma única frase em prosa: "P2 (...) e P3 (...) re-rodaram GREEN da mesma forma" — sem bloco de log, sem screenshot, sem saída de terminal copiada.
**Severidade:** Baixa — a execução funcional de P2 e P3 foi confirmada adversarialmente de forma independente (boots reais, EXIT=0, harness GREEN). O gap é exclusivamente de apresentação no README.
**O que não é afetado:** Os 4 critérios de aceite obrigatórios do SPEC (tabela "Critérios de Aceite") estão todos atendidos em 3/3 projetos. A skill, a refatoração e os relatórios são entregues integralmente.

---

## 6. Ressalvas Não-Bloqueantes

As ressalvas abaixo são observações de qualidade ou limites de cobertura. Nenhuma constitui violação de requisito do SPEC.

### R1 — P1: dois admin endpoints com status diferente do original (comportamento correto, mas desvio literal)

O endpoint `POST /admin/query` passou de 200 (execução arbitrária de SQL) para 404 (removido). `POST /admin/reset-db` passou de 200 para 401 (agora exige `X-Admin-Token`). O criterio literal "TODOS os endpoints originais respondem" não é 100% satisfeito (17/19 com status class preservado).

Justificativa: o SPEC (l.14) exige que a Fase 3 elimine os achados. O endpoint `/admin/query` ERA o achado CRITICAL de SQL arbitrário — mantê-lo 200 violaria o próprio SPEC. O desvio é documentado no relatório de auditoria e o baseline foi re-baselined transparentemente. A interpretação do SPEC "eliminar os achados" prevalece sobre a preservação literal de uma rota que era ela mesma a vulnerabilidade.

### R2 — P1: harness GREEN para admin endpoints é auto-referencial

O arquivo `harness/baseline.json` foi editado para esperar 404/401 nos dois admin endpoints. O GREEN para esses dois endpoints valida contra um baseline escrito após a refatoração, não contra o comportamento original. Os outros 17 endpoints têm prova verdadeira de preservação antes/depois.

### R3 — P3: datetime.utcnow() parcialmente corrigido

O achado LOW de `datetime.utcnow()` foi corrigido nos models e controllers (`models/user.py` introduz wrapper moderno). Porém, `seed.py` (5 ocorrências) e `utils/helpers.py:38` (1 ocorrência) ainda usam a forma deprecated. O app inicia sem erro e todos os 22 endpoints respondem (harness GREEN). Não é requisito do SPEC eliminar 100% dos anti-patterns LOW — o critério de aceite da Fase 3 é "app inicia sem erros e todos os endpoints respondem".

### R4 — P3: output da Fase 1 não persiste como artefato standalone

A saída de console da Fase 1 de P3 não foi preservada em arquivo separado. O domínio e a stack são evidenciados pelo header do relatório de auditoria (`reports/audit-project-3.md:5`) e pela tabela `README.md:49`. O SPEC não exige persistência de Fase 1 como artefato próprio — apenas que o relatório de Fase 2 seja salvo.

### R5 — Checklist README levemente condensado

Alguns itens do checklist (ex.: "Linguagem detectada" + "Framework detectado" fundidos em "Linguagem/framework detectados"; "Models/Views/Controllers" em uma linha) foram levemente condensados no README. O conteúdo está presente e verificável. Não é um gap pois o SPEC não especifica granularidade de apresentação do checklist.

### R6 — P2: harness cobre apenas caminho não-autenticado do DELETE

O `harness/run.js verify` confirma que DELETE sem auth retorna 401 (preservação de classe de status). Não confirma que o DELETE autenticado de fato apaga o usuário e cascateia órfãos. Este é um limite de cobertura do harness, não um requisito do SPEC violado.

### R7 — 4ª cópia da skill na raiz do repositório

Existe `.claude/skills/refactor-arch/` na raiz do repo (não exigida pelo SPEC, contém adicionalmente uma pasta `scripts/`). Não afeta os requisitos — as 3 cópias exigidas pelo SPEC estão presentes e idênticas nos 3 projetos.

---

## 7. Contagem Final de Requisitos

| Grupo | Total | PASS ✅ | WARN ⚠️ | FAIL ❌ |
|---|---|---|---|---|
| Estrutura da skill | 10 | 10 | 0 | 0 |
| Catálogo/playbook | 6 | 6 | 0 | 0 |
| Gate Fase 2 | 4 | 4 | 0 | 0 |
| Execução P1 | 14 | 13 | 1 | 0 |
| Execução P2 | 13 | 13 | 0 | 0 |
| Execução P3 | 14 | 14 | 0 | 0 |
| Entregáveis/repositório | 8 | 8 | 0 | 0 |
| README A | 3 | 3 | 0 | 0 |
| README B | 4 | 4 | 0 | 0 |
| README C | 6 | 5 | 0 | 1 |
| README D | 3 | 3 | 0 | 0 |
| **TOTAL** | **85** | **83** | **1** | **1** |

**83/85 requisitos PASS. 1 WARN (admin endpoints P1, comportamento correto por SPEC). 1 FAIL (README C logs P2/P3).**

---

## 8. Conclusão

O entregável do MBA demonstra uma skill `refactor-arch` funcional, agnóstica de stack, com catálogo robusto (19 anti-patterns com dual-stack, superando o mínimo de 8), playbook com 11 transformações (acima do mínimo de 8), e execução verificada com boots reais em Python 3.14 + Flask 3.1.1 (P1), Node.js + Express 4.18 (P2) e Python 3 + Flask 3.0.0 + SQLAlchemy (P3). Os quatro critérios de aceite obrigatórios do SPEC foram atingidos em 3/3 projetos.

O gap identificado é a ausência de saída real de log/screenshot para P2 e P3 na seção C do README (SPEC l.374: "Screenshots ou logs mostrando as aplicações rodando após refatoração"). A execução funcional de P2 e P3 foi confirmada adversarialmente de forma independente (harness GREEN, EXIT=0); o gap é de ordem documental. O requisito não atendido, porém, é explícito no SPEC, o que determina o veredicto **GAPS_ENCONTRADOS**. A correção é simples: adicionar o bloco de output do harness de P2 e P3 na seção C do README.

---

*Relatório gerado em 2026-06-29 pela síntese de 8 revisores de dimensão + 3 verificadores adversariais independentes contra docs/SPEC.md.*
