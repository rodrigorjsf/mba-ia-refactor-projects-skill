# Baseline de achados — investigação inicial dos 3 projetos

Achados **localizados** (arquivo:linha) descobertos na leitura inicial do código
durante o planejamento. É **insumo** para a Análise Manual (SPEC §1 / [ROADMAP Fase 1](../ROADMAP.md#fase-1--análise-manual-dos-3-projetos-spec-1)) e
para semear o catálogo da skill — **não** é a análise final. A Fase 1 deve
confirmar, expandir e completar (sobretudo o Projeto 3, lido só parcialmente aqui).

Severidades conforme [CONTEXT.md](../../CONTEXT.md).

---

## Projeto 1 — code-smells-project (Python/Flask)

| Severidade | Achado | Arquivo:linha | Por que importa |
|---|---|---|---|
| CRITICAL | SQL Injection por concatenação de string | `models.py:28,48-49,109-111,289-297` (e outros) | Input do usuário concatenado direto na query → injeção total |
| CRITICAL | Endpoint de SQL arbitrário | `app.py:59-78` (`/admin/query`) | Executa SQL cru do request; RCE-equivalente no banco |
| CRITICAL | `SECRET_KEY` hardcoded | `app.py:7` | Segredo no código; sessões forjáveis |
| CRITICAL | Senha em texto plano (storage + retorno + login) | `models.py:122-131,79-86,105-120` · `controllers.py:128-134` | Senhas gravadas/comparadas/retornadas sem hash |
| CRITICAL | Segredo e debug vazados no `/health` | `controllers.py:285-289` | Expõe `secret_key`, `debug`, ambiente publicamente |
| HIGH | God Class | `models.py` (1-315) | Dados + negócio + relatório de 4 domínios num arquivo |
| HIGH | Efeitos colaterais / negócio no controller | `controllers.py:208-210,247-250` | Email/SMS/push (como `print`) dentro do handler |
| HIGH | Debug mode ligado | `app.py:8,88` | `DEBUG=True` em "produção" → debugger executa código |
| HIGH | Endpoint destrutivo sem auth | `app.py:47-57` (`/admin/reset-db`) | Apaga todas as tabelas sem autenticação |
| MEDIUM | Query N+1 | `models.py:187-199,219-231` | Cursores aninhados por item de pedido |
| MEDIUM | `except Exception` vazando `str(e)` | `controllers.py` (todos os handlers) | Detalhe interno exposto ao cliente |
| LOW | Magic numbers | `models.py:257-262` | Faixas de desconto 10000/5000/1000 soltas |
| LOW | `print()` como log | `controllers.py`, `models.py` (vários) | Sem logging estruturado |
| LOW | Duplicação | `models.py:171-201` vs `203-233` | `get_pedidos_usuario` ≈ `get_todos_pedidos` |

## Projeto 2 — ecommerce-api-legacy (Node/Express)

| Severidade | Achado | Arquivo:linha | Por que importa |
|---|---|---|---|
| CRITICAL | Credenciais hardcoded | `utils.js:1-7` | `dbPass`, `paymentGatewayKey` (`pk_live_...`), `smtpUser` no código |
| CRITICAL | Hashing de senha caseiro e fraco | `utils.js:17-23` (`badCrypto`) | base64 em loop, trunca em 10 chars; trivial de quebrar |
| CRITICAL | Dado sensível em log | `AppManager.js:45` | Loga número do cartão + chave do gateway |
| HIGH | God Class | `AppManager.js` (1-141) | Init de DB + rotas + negócio + pagamento numa classe |
| HIGH | Callback hell / pyramid of doom | `AppManager.js:37-77` | Callbacks de DB aninhados no checkout |
| HIGH | Estado global mutável | `utils.js:9-10` | `globalCache`, `totalRevenue` compartilhados |
| HIGH | Validação de pagamento ingênua | `AppManager.js:46` | Cartão "válido" se começa com "4" |
| MEDIUM | Query N+1 | `AppManager.js:80-129` | Relatório: query por curso × matrícula × usuário/pagamento |
| MEDIUM | Dados órfãos no delete (sem cascade/tx) | `AppManager.js:131-137` | Deleta usuário, deixa matrículas/pagamentos (o próprio código admite) |
| MEDIUM | Banco em memória perde dados | `AppManager.js:7` (`:memory:`) | Estado some a cada restart |
| LOW | Nomes crípticos | `AppManager.js:29-33` | `u`, `e`, `p`, `cid`, `cc` |
| LOW | `console.log` como log | `utils.js:13` · `AppManager.js:45` | Sem logging estruturado |

## Projeto 3 — task-manager-api (Python/Flask, parcialmente organizado)

> **Cobertura parcial.** Lidos só `app.py` e `services/notification_service.py`.
> A Fase 1 deve completar lendo `routes/`, `models/`, `utils/helpers.py`,
> `database.py` e `seed.py`.

| Severidade | Achado | Arquivo:linha | Por que importa |
|---|---|---|---|
| CRITICAL | Credenciais SMTP hardcoded | `services/notification_service.py:10` | `email_password='senha123'` no código |
| CRITICAL | `SECRET_KEY` hardcoded | `app.py:13` | Segredo no código |
| HIGH | Debug mode ligado | `app.py:34` | `debug=True` |
| HIGH | API deprecated: `datetime.utcnow()` | `services/notification_service.py:35` | Depreciada no Python 3.12+ → `datetime.now(timezone.utc)` |
| MEDIUM | Efeito externo real (SMTP) em endpoint | `services/notification_service.py:12-25` | Chamada `smtplib` viva ao `smtp.gmail.com` ao atribuir task — ver risco no [ADR-0003](../adr/0003-validacao-harness-como-gate-tdd.md) |
| MEDIUM | `db.create_all()` em tempo de import | `app.py:30-31` | Efeito colateral no import do módulo |

---

## Cobertura mínima (SPEC §1: ≥5 por projeto, ≥1 CRIT/HIGH, ≥2 MED, ≥2 LOW)

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Atende mínimo? |
|---|:--:|:--:|:--:|:--:|:--:|
| code-smells-project | 5 | 4 | 2 | 3 | ✅ |
| ecommerce-api-legacy | 3 | 4 | 3 | 2 | ✅ |
| task-manager-api (parcial) | 2 | 2 | 2 | 0 | ⚠️ completar LOW na Fase 1 |
