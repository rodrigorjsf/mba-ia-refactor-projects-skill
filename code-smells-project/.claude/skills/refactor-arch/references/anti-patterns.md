# Catálogo de anti-patterns

Cada entrada: **princípio agnóstico** + **sinais de detecção acionáveis por stack** + impacto. Os sinais são o que você procura no código frio — regex/AST, não "código ruim". Severidade conforme `CONTEXT.md`. Cruze **todo** o catálogo na Fase 2; depois rode a seção de **APIs deprecated**.

---

## CRITICAL

### SQL Injection por concatenação
**Princípio:** input nunca entra na query por concatenação/interpolação de string; só por parâmetro.
**Flask/Python:** `cursor.execute("... " + var)`, `execute(f"... {var}")`, `"WHERE x = '" + s + "'"`.
**Express/Node:** `db.run("... " + v)`, template string `` `... ${v}` `` dentro de `query/run/get/all`.
**Impacto:** vazamento/escrita arbitrária no banco; comprometimento total.

### Endpoint de SQL arbitrário / operação destrutiva sem auth
**Princípio:** nenhum endpoint executa SQL cru do request nem faz operação destrutiva sem autenticação/autorização.
**Flask/Python:** rota que faz `cursor.execute(request_json["sql"])`; `DELETE FROM ...` num `/admin/...` sem checagem de auth.
**Express/Node:** `app.post('/admin/query', ...)` repassando corpo ao driver; `DELETE` route sem middleware de auth.
**Impacto:** RCE-equivalente no banco; perda total de dados.

### Credenciais / segredos hardcoded
**Princípio:** segredos vivem no ambiente, nunca no código.
**Flask/Python:** `app.config["SECRET_KEY"] = "..."`, `email_password = 'senha123'`, senha/token literal.
**Express/Node:** `const config = { dbPass: "...", paymentGatewayKey: "pk_live_..." }`.
**Impacto:** sessões forjáveis, chave de pagamento/SMTP vazada no repo.

### Senha em texto plano ou hash caseiro/fraco
**Princípio:** senha é guardada e comparada só por hash adaptativo (bcrypt/argon2/scrypt), nunca plana, caseira ou com hash rápido (md5/sha1).
**Flask/Python:** coluna `senha`/`password` recebendo o valor cru; comparação `senha == row["senha"]`; `hashlib.md5(pwd)`.
**Express/Node:** `badCrypto`/loop de `Buffer.from(pwd).toString('base64')`; `pass` salvo direto.
**Impacto:** vazamento do banco expõe todas as senhas; trivial de quebrar.

### Dado sensível exposto em resposta ou log
**Princípio:** segredo/PII (senha, hash, nº de cartão, secret key) nunca sai no corpo HTTP nem em log.
**Flask/Python:** `to_dict()` que inclui `password`; `/health` retornando `secret_key`/`debug`; `SELECT *` de usuários devolvendo `senha`.
**Express/Node:** `console.log(\`...${cardNumber}...${gatewayKey}\`)`; resposta JSON com campo de senha.
**Impacto:** vazamento direto de credenciais e dados pessoais.

---

## HIGH

### God Class / God Module
**Princípio:** uma unidade não acumula persistência + negócio + roteamento de vários domínios.
**Flask/Python:** um `models.py` com SQL, validação, relatório e formatação de 4 domínios; arquivo com centenas de linhas e responsabilidades misturadas.
**Express/Node:** uma classe `AppManager` que faz `initDb` + `setupRoutes` + pagamento + relatório.
**Impacto:** impossível testar em isolamento; qualquer mudança arrisca tudo.

### Lógica de negócio / efeito colateral no controller ou rota
**Princípio:** o handler de requisição orquestra; regra de negócio e efeito externo ficam em model/service.
**Flask/Python:** envio de e-mail/SMS/push (mesmo como `print`) dentro do handler; cálculo de negócio no controller.
**Express/Node:** lógica de pagamento, hashing e enrol no corpo da rota `/checkout`.
**Impacto:** acoplamento, duplicação, efeito não-testável preso ao HTTP.

### Debug mode ligado em produção
**Princípio:** o debugger do framework vem de config de ambiente, default desligado.
**Flask/Python:** `app.config["DEBUG"] = True`, `app.run(debug=True)`.
**Express/Node:** stack trace de erro vazado por default; `NODE_ENV` não tratado.
**Impacto:** o debugger interativo executa código arbitrário; vaza stack e estado interno.

### Estado global mutável
**Princípio:** estado compartilhado mutável em nível de módulo vira fonte de corrida e acoplamento.
**Flask/Python:** `db_connection = None` global reusado; contadores/cache de módulo.
**Express/Node:** `let globalCache = {}`, `let totalRevenue = 0` exportados e mutados.
**Impacto:** corrida entre requests, vazamento de estado, teste impossível.

### Validação de segurança ingênua
**Princípio:** decisão de segurança (pagamento aprovado, permissão) não se baseia em heurística frágil.
**Flask/Python:** "admin" inferido de campo do request sem checagem; aprovação por prefixo.
**Express/Node:** `status = cc.startsWith("4") ? "PAID" : "DENIED"`.
**Impacto:** bypass trivial de pagamento/autorização.

---

## MEDIUM

### Query N+1
**Princípio:** não emita uma query por item dentro de um loop sobre um resultado; use JOIN/IN/batch.
**Flask/Python:** cursores aninhados — `for pedido: for item: SELECT ... WHERE id = item`.
**Express/Node:** `courses.forEach(c => db.all(enrollments) ... forEach(enr => db.get(user) ...))`.
**Impacto:** latência cresce linear com os dados; gargalo sob carga.

### Tratamento de erro vazando detalhe interno
**Princípio:** o cliente recebe erro padronizado; o detalhe vira log interno.
**Flask/Python:** `except Exception as e: return jsonify({"erro": str(e)}), 500` repetido em cada handler; `except:` nu engolindo a causa.
**Express/Node:** `res.status(500).send(err.message)`; ausência de middleware de erro.
**Impacto:** vaza estrutura interna; mascara bugs; duplicação massiva.

### Falta de integridade referencial no delete
**Princípio:** apagar um agregado trata os dependentes (cascade/transação), sem deixar órfãos.
**Flask/Python:** `DELETE FROM usuarios` sem tocar pedidos/itens relacionados.
**Express/Node:** `DELETE FROM users WHERE id = ?` deixando enrollments/payments (o código às vezes admite no texto).
**Impacto:** dados órfãos, relatórios inconsistentes.

### Efeito colateral em tempo de import
**Princípio:** importar um módulo não deve abrir conexão, criar schema nem fazer I/O.
**Flask/Python:** `db.create_all()` no corpo do módulo; `get_db()` que conecta no import.
**Express/Node:** `new Database(...)` + `initDb()` rodando no carregamento do módulo.
**Impacto:** ordem de import frágil, teste difícil, efeito surpresa.

### Validação ausente ou duplicada na rota
**Princípio:** validação de input mora num lugar (schema/service), não copiada por handler.
**Flask/Python:** o mesmo bloco de checagem `if not x: return 400` repetido em create/update.
**Express/Node:** validação inline repetida por rota, sem schema.
**Impacto:** regras divergem entre endpoints; manutenção cara.

---

## LOW

### Log ad-hoc via print/console.log
**Princípio:** use um logger configurável, não stdout cru.
**Flask/Python:** `print("...")` como log de evento/erro.
**Express/Node:** `console.log(...)` como log de aplicação.
**Impacto:** sem nível, sem destino, sem correlação.

### Magic numbers
**Princípio:** literal numérico com significado de negócio vira constante nomeada.
**Flask/Python:** faixas de desconto `10000/5000/1000` soltas; limites mágicos.
**Express/Node:** thresholds numéricos inline.
**Impacto:** intenção obscura; mudança arriscada.

### Nomes crípticos
**Princípio:** identificador descreve o que carrega.
**Flask/Python:** `e`, `d`, `tmp` para entidades de domínio.
**Express/Node:** `u`, `e`, `p`, `cid`, `cc` para user/email/password/courseId/card.
**Impacto:** legibilidade ruim, erro fácil.

### Código duplicado
**Princípio:** bloco quase-idêntico vira função única parametrizada.
**Flask/Python:** `get_pedidos_usuario` ≈ `get_todos_pedidos` mudando só o filtro.
**Express/Node:** handlers que repetem o mesmo monte de query/format.
**Impacto:** correção precisa ser feita em N lugares.

---

## APIs deprecated (detecção obrigatória)

Identifique uso de API obsoleta/insegura e recomende o equivalente moderno.

| Deprecated | Equivalente moderno | Onde |
|---|---|---|
| `datetime.utcnow()` | `datetime.now(datetime.timezone.utc)` | Python 3.12+ deprecou `utcnow()` (naive) |
| `hashlib.md5` / `sha1` p/ senha | `bcrypt` / `argon2` / `werkzeug.security.generate_password_hash` | hash rápido é inseguro para senha |
| API de callback do `sqlite3` (Node) | `node:sqlite` / wrapper `promisify` + async/await | callback hell, erro silencioso |
| `body-parser` standalone (Express) | `express.json()` nativo | embutido desde Express 4.16 |
| `datetime.strptime` solto p/ ISO | `datetime.fromisoformat` | parsing ISO nativo e estrito |
| `var` / callbacks aninhados (JS) | `const`/`let` + `async/await` | escopo e fluxo previsíveis |

Cada uso encontrado vira um **achado** no relatório (severidade conforme o risco — `datetime.utcnow()` em si é LOW/MEDIUM; md5 para senha é CRITICAL), com o equivalente moderno na recomendação.
