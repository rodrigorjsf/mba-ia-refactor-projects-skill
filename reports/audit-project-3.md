================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python 3 + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1 (SQLite, sqlite:///tasks.db)
Files:   13 analyzed | ~900 lines of code

## Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 4 | LOW: 4

## Findings

### [CRITICAL] Credenciais / segredos hardcoded
File: app.py:13 ; services/notification_service.py:9-10
Description: `SECRET_KEY` da aplicação Flask embutido no código (`app.config['SECRET_KEY'] = 'super-secret-key-123'`) e credencial SMTP literal no service (`self.email_user = 'taskmanager@gmail.com'`, `self.email_password = 'senha123'`).
Impact: segredo versionado no repositório; sessões/tokens forjáveis e conta de e-mail comprometida por qualquer um com acesso ao código.
Recommendation: mover para `config/` lido de `os.environ`, com default só-de-dev claramente marcado e exigência da env em produção. Ver playbook §3.

### [CRITICAL] Senha com hash fraco (md5) + API deprecated para senha
File: models/user.py:3,27-29,31-32
Description: `set_password` e `check_password` usam `hashlib.md5(pwd.encode()).hexdigest()`. MD5 é hash rápido, não-adaptativo e quebrável; o catálogo de APIs deprecated marca `hashlib.md5` para senha como inseguro.
Impact: vazamento do banco expõe todas as senhas (trivialmente quebráveis por rainbow table / brute force).
Recommendation: trocar por `werkzeug.security.generate_password_hash` / `check_password_hash` (ou bcrypt/argon2) e **migrar o seed** para o novo esquema (senão login regride 200→401). Ver playbook §4.

### [CRITICAL] Dado sensível (hash de senha) exposto na resposta HTTP
File: models/user.py:16-25 (campo `password` em `to_dict`)
Description: `User.to_dict()` inclui o campo `password`. É devolvido ao cliente em `GET /users/<id>` (user_routes.py:33), `POST /users` (user_routes.py:85), `PUT /users/<id>` (user_routes.py:129) e aninhado em `POST /login` sob a chave `user` (user_routes.py:209).
Impact: vazamento direto do hash de credenciais em múltiplos endpoints, inclusive no login não-autenticado.
Recommendation: serializer que omite `password` (e qualquer segredo/PII). Ver playbook §10. Atenção: em `/login` o campo é aninhado — verificar manualmente a remoção, pois o harness é cego a campos aninhados.

### [HIGH] Debug mode ligado
File: app.py:34
Description: `app.run(debug=True, host='0.0.0.0', port=5000)` — debugger interativo do Werkzeug habilitado e exposto em `0.0.0.0`.
Impact: o console de debug do Werkzeug permite execução de código arbitrário e vaza stack/estado interno se atingido em produção.
Recommendation: `debug` vindo de env, default desligado (`app.run(debug=settings.DEBUG)`). Ver playbook §9.

### [HIGH] Lógica de negócio nos controllers/rotas
File: routes/task_routes.py:30-48,71-80,274-297 ; routes/user_routes.py:171-180 ; routes/report_routes.py:13-101,104-155
Description: regras de domínio vivem dentro dos handlers HTTP: cálculo de "overdue" duplicado em 4 lugares (task_routes 30-48 e 71-80, user_routes 171-180, report_routes 34-43 e 132-135), agregação de estatísticas e montagem de relatório inteiramente no handler (`task_stats`, `summary_report`, `user_report`), serialização manual de task repetindo `to_dict`.
Impact: regra de negócio acoplada ao HTTP, não testável em isolamento, divergência entre cópias; viola a separação MVC (controller deve orquestrar, não conter a regra).
Recommendation: mover a regra para o Model (ex.: `Task.is_overdue`, já existente mas não usado) e a agregação para um service/controller; rota só roteia e serializa. Ver mvc-guidelines e playbook §2/§5.

### [MEDIUM] Query N+1
File: routes/task_routes.py:41-57 ; routes/report_routes.py:55-68
Description: em `get_tasks`, para cada task emite-se `User.query.get` e `Category.query.get` individuais dentro do loop; em `summary_report`, para cada usuário emite-se uma query `Task.query.filter_by(user_id=...)` por iteração.
Impact: latência cresce linear com o volume de dados; gargalo sob carga.
Recommendation: usar JOIN/`selectinload`/agregação única em vez de uma query por item. Ver playbook §7.

### [MEDIUM] Tratamento de erro espalhado e vazando detalhe / `except` nu
File: routes/task_routes.py:62,151-154,236-238 ; routes/user_routes.py:130-132,149-151 ; routes/report_routes.py:186-188,207-209,221-223
Description: `try/except` repetido por handler devolvendo 500 genérico, `except:` nu engolindo a causa (task_routes:62, 236; user_routes:130, 149; report_routes:186, 207, 221) e `print(str(e))` como log de erro. Não há tratamento de erro centralizado.
Impact: mascara bugs, duplica código, dificulta diagnóstico; ausência de ponto único de erro.
Recommendation: `@app.errorhandler(Exception)` central que loga e devolve `{"error": "Erro interno"}`, removendo os try/except locais. Ver playbook §8.

### [MEDIUM] Efeito colateral em tempo de import
File: app.py:30-31
Description: `with app.app_context(): db.create_all()` executa no corpo do módulo — criar schema acontece ao importar `app`.
Impact: ordem de import frágil, efeito surpresa, dificulta teste e reuso do objeto app sem disparar I/O.
Recommendation: inicialização explícita (app factory / composition root); schema criado por comando/CLI, não no import. Ver playbook §11.

### [MEDIUM] Validação duplicada e validador paralelo morto
File: routes/task_routes.py:96-114 vs 166-184 ; utils/helpers.py:57-108,110-116
Description: as mesmas regras de validação de task (título 3-200, status válido, prioridade 1-5) são copiadas entre `create_task` e `update_task`; `utils/helpers.py` define um `process_task_data` e constantes (`VALID_STATUSES`, `MAX_TITLE_LENGTH`, `MIN_PASSWORD_LENGTH`...) que reimplementam essas regras mas **não são usados** pelas rotas.
Impact: regras divergem entre endpoints; manutenção cara; código morto confunde.
Recommendation: centralizar validação num schema/service único (marshmallow já está nas deps) e consumir as constantes existentes.

### [LOW] Log ad-hoc via print
File: routes/task_routes.py:149,153,219 ; routes/user_routes.py:83,89,147 ; services/notification_service.py:21,24 ; utils/helpers.py:38-41
Description: eventos e erros logados com `print(...)` em vez de um logger configurável.
Impact: sem nível, destino ou correlação; ruído no stdout.
Recommendation: usar `logging`/`app.logger`.

### [LOW] Nomes crípticos
File: routes/task_routes.py:16,268,283 ; routes/user_routes.py:14,37,141,161 ; routes/report_routes.py:33,55,119,161
Description: identificadores de domínio nomeados como `t`, `u`, `c`, `d`, `p`, `e` em loops e handlers.
Impact: legibilidade ruim, erro fácil.
Recommendation: nomes descritivos (`task`, `user`, `category`).

### [LOW] Magic numbers inline
File: routes/task_routes.py:96,99,113 ; routes/user_routes.py:64 ; routes/report_routes.py (priority 1..5 em 24-28)
Description: limites de negócio (título 3/200, prioridade 1/5, senha mínima 4, faixas de prioridade) hardcoded inline, apesar de existirem constantes nomeadas equivalentes em `utils/helpers.py:110-116`.
Impact: intenção obscura; mudança arriscada e dispersa.
Recommendation: usar as constantes nomeadas.

### [LOW] APIs deprecated de datetime
File: models/user.py:14 ; models/task.py:15-16,52 ; routes/task_routes.py:31,72,136,203,215,285 ; routes/user_routes.py:172 ; routes/report_routes.py:35,42,45,71,133 ; utils/helpers.py:38,45,48
Description: uso pervasivo de `datetime.utcnow()` (deprecado no Python 3.12, retorna naive) e de `datetime.strptime(...)` para parse de datas ISO.
Impact: warnings de deprecação, datetimes naive sujeitos a bug de fuso; parsing ISO frágil.
Recommendation: `datetime.now(datetime.timezone.utc)` no lugar de `utcnow()`; `datetime.fromisoformat(...)` para ISO.

================================
Total: 13 findings
================================

Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]
