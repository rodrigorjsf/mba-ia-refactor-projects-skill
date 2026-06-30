================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express 4.18 + SQLite (sqlite3 raw callback driver, in-memory)
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 4 | HIGH: 4 | MEDIUM: 4 | LOW: 3

## Findings

### [CRITICAL] Credenciais / segredos hardcoded
File: src/utils.js:2-5
Description: The `config` object embeds production secrets in source: `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"`, plus `dbUser` and `smtpUser`. A literal `pk_live_...` key is a real payment credential.
Impact: Anyone with repo access (or a leaked clone) gets the live payment key and DB password; forgeable charges, lateral movement. Secrets in VCS history are effectively permanent.
Recommendation: Move every secret to `process.env`, read in a `config/` module with dev-only clearly-marked defaults and fail-fast in production. Playbook #3 (segredo hardcoded -> config do ambiente).

### [CRITICAL] Senha com hash caseiro/fraco e seed em texto plano
File: src/utils.js:17-23 (badCrypto); src/AppManager.js:68 (use on signup); src/AppManager.js:18 (seed pass '123')
Description: Passwords are "hashed" by `badCrypto`, a custom loop concatenating `Buffer.from(pwd).toString('base64')` and truncating to 10 chars — non-adaptive, collision-prone, trivially reversible. The seeded user is stored with the literal plaintext `'123'`.
Impact: A DB dump exposes all passwords; the homemade scheme offers no real protection and the seed is plaintext. Matches catalog "Senha em texto plano ou hash caseiro/fraco".
Recommendation: Replace with an adaptive KDF. Prefer Node stdlib `crypto.scryptSync`/`scrypt` (salted, `scrypt$N$salt$hash` format) to avoid native-build friction; migrate the seed to the new scheme in the same change. Playbook #4 (migre os dados semeados).

### [CRITICAL] Dado sensível (nº de cartão + chave de gateway) em log
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)` writes the full card number (PAN) and the live payment gateway key to stdout on every checkout.
Impact: PCI-relevant cardholder data and a live secret leak into logs/aggregators — direct credential and PII exposure. Matches catalog "Dado sensível exposto em resposta ou log".
Recommendation: Remove the secret-bearing log; if a payment trace is needed, log only a masked PAN suffix and never the gateway key. Move the call into an isolated payment service. Playbook #10.

### [CRITICAL] Operação destrutiva sem autenticação (DELETE de usuário)
File: src/AppManager.js:131-137
Description: `app.delete('/api/users/:id', ...)` runs `DELETE FROM users WHERE id = ?` with no authentication/authorization whatsoever — any caller can wipe any user. The handler's own response text admits it leaves dependent rows dirty.
Impact: Unauthenticated mass data destruction; RCE-equivalent blast radius on the data layer. Matches catalog CRITICAL "Endpoint ... operação destrutiva sem auth".
Recommendation: INTENTIONAL STATUS CHANGE — gate the endpoint behind admin-token auth (env `ADMIN_TOKEN`, dev-only default, header required regardless). The unauthenticated harness call therefore moves **200 -> 401**; this endpoint is re-baselined (`harness/baseline.json`) and documented here per mvc-guidelines › "exceção ao harness verde". Also fix referential integrity for the authorized path (see [MEDIUM] orphans). Playbook #2 (camadas) + middleware de auth.

### [HIGH] God Class / God Module (AppManager)
File: src/AppManager.js:4-141
Description: A single `AppManager` class owns schema creation (`initDb`), routing (`setupRoutes`), payment processing, enrollment, audit logging, and the financial report across 4 domains.
Impact: No unit can be tested in isolation; every change risks the whole surface. Matches catalog HIGH "God Class".
Recommendation: Split into Model (per entity), Controller (per resource), routes (View), and a payment Service; keep DB access only in Models. Playbook #2.

### [HIGH] Lógica de negócio e efeito colateral no controller/rota
File: src/AppManager.js:43-78
Description: The `/checkout` route handler inlines payment decision, password hashing, user creation, enrollment, payment record, and audit write — business rules and side effects live in the HTTP handler.
Impact: Tight coupling, non-testable effects bound to HTTP, duplication. Matches catalog HIGH "Lógica de negócio / efeito colateral no controller".
Recommendation: Move orchestration to a controller and the payment effect to a `services/payment.service.js`; the handler only validates input and shapes the response. Playbook #5.

### [HIGH] Estado global mutável
File: src/utils.js:9-10, 12-15
Description: Module-level `let globalCache = {}` and `let totalRevenue = 0` are exported and mutated (`logAndCache` writes into `globalCache`). Shared mutable module state.
Impact: Race conditions across concurrent requests, state leakage, impossible isolated testing. Matches catalog HIGH "Estado global mutável".
Recommendation: Remove the global cache or encapsulate it behind an injected service instance with a clear lifecycle; no exported mutable module state. Playbook #2/#5.

### [HIGH] Validação de segurança ingênua (aprovação de pagamento por prefixo)
File: src/AppManager.js:46
Description: Payment approval is decided by `cc.startsWith("4") ? "PAID" : "DENIED"` — a string-prefix heuristic standing in for a real gateway authorization.
Impact: Trivial bypass: any card starting with "4" is "paid". Matches catalog HIGH "Validação de segurança ingênua".
Recommendation: Delegate authorization to a payment Service with an explicit, stubbable interface; never derive a security decision from a prefix. Playbook #5. (Behavior of the approve/deny branches must be preserved while relocated.)

### [MEDIUM] Query N+1 no relatório financeiro
File: src/AppManager.js:83-127
Description: The report loops `courses.forEach` -> per course `db.all(enrollments)` -> per enrollment `db.get(user)` + `db.get(payment)` — one query per row, nested.
Impact: Latency grows linearly with data; bottleneck under load. Matches catalog MEDIUM "Query N+1".
Recommendation: Replace with a single JOIN across courses/enrollments/users/payments and aggregate in memory. Playbook #7. (Response element shape `{course, revenue, students:[{student, paid}]}` must be preserved; `students[]` is nested so verify by hand.)

### [MEDIUM] Tratamento de erro ausente/duplicado, sem middleware central
File: src/AppManager.js:38, 41, 51, 55, 70, 84
Description: Each callback repeats ad-hoc `res.status(500).send("Erro DB" / "Erro Matrícula" / ...)`; there is no centralized Express error middleware, and DB errors are inconsistently handled (some callbacks ignore `err`).
Impact: Duplicated handling, inconsistent responses, masked bugs. Matches catalog MEDIUM "Tratamento de erro vazando detalhe interno".
Recommendation: Add a final `app.use((err, req, res, next) => ...)` error middleware returning a standardized body; controllers stop hand-rolling 500s. Playbook #8.

### [MEDIUM] Falta de integridade referencial no DELETE (órfãos)
File: src/AppManager.js:133-135
Description: `DELETE FROM users` removes the user but leaves `enrollments` and `payments` rows orphaned — the response string literally admits "as matrículas e pagamentos ficaram sujos no banco".
Impact: Orphaned dependents, inconsistent reports. Matches catalog MEDIUM "Falta de integridade referencial no delete".
Recommendation: Delete dependents in a transaction (or cascade) inside the Model. Playbook #2 (Model owns persistence).

### [MEDIUM] [Deprecated API] sqlite3 callback driver / callback hell
File: src/AppManager.js:37-77 (nested `db.get`/`db.run` pyramid)
Description: The legacy `sqlite3` callback API drives a 5-level nested-callback pyramid in `/checkout`; errors are easy to drop silently (several callbacks ignore `err`).
Impact: Callback hell, silent error paths, unmaintainable control flow. Catalog "APIs deprecated" row: callback API do sqlite3 (Node).
Recommendation: Promisify the driver (`util.promisify` over `db.get/run/all`) or move to `node:sqlite`, and use linear `async/await` in the controller/model with one try/catch. Playbook #6.

### [LOW] Nomes crípticos
File: src/AppManager.js:29-33
Description: `u, e, p, cid, cc` stand for user/email/password/courseId/card.
Impact: Poor readability, easy to mis-edit. Matches catalog LOW "Nomes crípticos".
Recommendation: Rename to descriptive identifiers as the logic moves into controller/model.

### [LOW] Magic numbers
File: src/utils.js:19-22 (10000, 2, 10); src/AppManager.js:46 (card prefix "4")
Description: Unexplained literals in `badCrypto` (iteration count, substring sizes) and the `"4"` approval prefix carry business meaning inline.
Impact: Obscured intent, risky changes. Matches catalog LOW "Magic numbers".
Recommendation: Most disappear with the scrypt/payment-service rewrite; any survivors become named constants.

### [LOW] Log ad-hoc via console.log
File: src/app.js:13; src/utils.js:13; src/AppManager.js:45
Description: Application/event logging via raw `console.log` with no level/destination/correlation.
Impact: No structured logging. Matches catalog LOW "Log ad-hoc via print/console.log".
Recommendation: Introduce a minimal configurable logger; route app events through it.

================================
Total: 15 findings
================================

Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]
