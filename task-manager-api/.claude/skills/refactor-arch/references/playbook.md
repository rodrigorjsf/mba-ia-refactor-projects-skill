# Playbook de refatoração

Transformações concretas, do achado ao código corrigido. Cada uma: princípio + antes/depois por stack. Aplique as que casam com os achados da Fase 2. Exemplos em Flask/SQLite e Express/SQLite; o princípio é o mesmo em qualquer stack.

---

## 1. SQL Injection → query parametrizada
**Princípio:** valores vão por placeholder; a string SQL é estática.

```python
# Antes (Flask)
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
# Depois
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
```
```js
// Antes (Express)
db.get("SELECT * FROM users WHERE email = '" + e + "'", cb)
// Depois
db.get("SELECT * FROM users WHERE email = ?", [e], cb)
```

---

## 2. God Class/Module → camadas MVC
**Princípio:** separe persistência (Model), orquestração (Controller) e roteamento (View/Rotas) por domínio.

```python
# Antes (Flask): models.py faz SQL + negócio + formatação de 4 domínios
# Depois:
# models/produto_model.py   -> só dados de produto
# controllers/produto_controller.py -> valida, chama o model, monta resposta
# views/routes.py           -> mapeia /produtos -> controller
```
```js
// Antes (Express): class AppManager faz initDb + setupRoutes + payment
// Depois:
// models/course.model.js, controllers/checkout.controller.js,
// services/payment.service.js, routes/checkout.routes.js, app.js (composition root)
```

---

## 3. Segredo hardcoded → config do ambiente
**Princípio:** segredo lido de env, com default seguro, fora do código.

```python
# Antes (Flask)
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
# Depois (config/settings.py)
import os
# Segredo real vem da env; o default é SÓ-DE-DEV (claramente marcado) para o app
# subir com um comando. Em produção, exija a env (falhe rápido se ausente).
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-troque-em-producao")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
```
```js
// Antes (Express)
const config = { dbPass: "senha_super_secreta_prod_123", paymentGatewayKey: "pk_live_..." };
// Depois
const config = { dbPass: process.env.DB_PASS, paymentGatewayKey: process.env.PAYMENT_KEY, port: process.env.PORT || 3000 };
```

---

## 4. Senha plana/caseira → hash adaptativo (migrando o seed!)
**Princípio:** armazene e compare só por hash adaptativo. **Migre os dados semeados** ou o login regride 200→401 (se o app não tem endpoint de login/auth, a migração é higiene de segurança, não protege contrato).

```python
# Antes (Flask): senha == row["senha"]  / hashlib.md5(pwd)
# Depois
from werkzeug.security import generate_password_hash, check_password_hash
user.password = generate_password_hash(pwd)              # no cadastro/seed
ok = check_password_hash(user.password, pwd)             # no login
# seed: re-grave os usuários existentes com generate_password_hash(...)
```
```js
// Antes (Express): badCrypto(pwd) base64 em loop
// Depois
const bcrypt = require('bcrypt');
const hash = await bcrypt.hash(pwd, 10);                 // cadastro/seed
const ok = await bcrypt.compare(pwd, user.pass);         // login
// Sem dependência nativa: Node stdlib `crypto.scryptSync(pwd, salt, 64)` com salt
// por usuário (formato `scrypt$salt$hash`) — KDF adaptativo, evita o build do bcrypt.
```

---

## 5. Lógica/efeito no handler → Service
**Princípio:** controller fino; efeito externo e caso de uso vão para um service isolado (stubável).

```python
# Antes (Flask): print("ENVIANDO EMAIL...") dentro do handler de pedido
# Depois
# services/notification_service.py
class NotificationService:
    def pedido_criado(self, pedido): ...   # efeito isolado, mockável no harness
# controller: notification.pedido_criado(pedido)
```
```js
// Antes (Express): pagamento + enrol + cobrança no corpo da rota /checkout
// Depois
// services/payment.service.js exporta processPayment(card, amount)
// o controller só orquestra: validate -> service -> resposta
```

---

## 6. Callback hell → async/await
**Princípio:** achate a pirâmide; erros sobem por `try/catch`.

```js
// Antes (Express): db.get(...=> db.get(...=> db.run(...=> db.run(...))))
// Depois: promisificar o driver e await em sequência
const { promisify } = require('util');
const get = promisify(db.get.bind(db)), run = promisify(db.run.bind(db));
const course = await get("SELECT * FROM courses WHERE id = ?", [cid]);
const user = await get("SELECT id FROM users WHERE email = ?", [e]);
// ... fluxo linear, um try/catch no controller
```
```python
# Flask é síncrono — o equivalente é extrair a cadeia para o model/service,
# uma chamada por passo, sem aninhar cursores no handler.
```

---

## 7. N+1 → JOIN/batch
**Princípio:** uma query com JOIN/IN no lugar de uma por item.

```python
# Antes (Flask): for pedido: for item: SELECT nome FROM produtos WHERE id = ?
# Depois
cursor.execute("""
  SELECT ip.*, p.nome FROM itens_pedido ip
  JOIN produtos p ON p.id = ip.produto_id WHERE ip.pedido_id = ?""", (pid,))
```
```js
// Antes (Express): courses.forEach -> enrollments.forEach -> users.get/payments.get
// Depois: um SELECT com JOIN entre courses/enrollments/users/payments,
// agrupando em memória — uma ida ao banco.
```

---

## 8. Erro espalhado → tratamento centralizado
**Princípio:** um ponto único formata o erro; handlers param de repetir try/except.

```python
# Antes (Flask): cada handler com except Exception: return jsonify({"erro": str(e)}), 500
# Depois (middlewares/error_handler.py)
@app.errorhandler(Exception)
def handle(e):
    app.logger.exception(e)
    return jsonify({"erro": "Erro interno"}), 500   # sem vazar str(e)
```
```js
// Antes (Express): res.status(500).send(err.message) por rota
// Depois: middleware final
app.use((err, req, res, next) => { logger.error(err); res.status(500).json({ error: "Erro interno" }); });
```

---

## 9. Debug ligado → gated por ambiente
**Princípio:** debug vem de env, default desligado.

```python
# Antes (Flask): app.run(debug=True) ; app.config["DEBUG"] = True
# Depois
app.run(debug=settings.DEBUG)        # settings.DEBUG lido de env, default False
```
```js
// Antes (Express): stack trace por default
// Depois: if (process.env.NODE_ENV === 'production') desliga detalhe de erro no handler
```

---

## 10. Dado sensível na resposta → serializer que omite segredo
**Princípio:** a camada de serialização decide o que sai; segredo/PII nunca.

```python
# Antes (Flask): to_dict() inclui "password"; /health devolve secret_key
# Depois
def to_dict(self):
    return {"id": self.id, "name": self.name, "email": self.email, "role": self.role}  # sem password
# /health: só {"status": "ok"} — nada de secret_key/debug
```
```js
// Antes (Express): JSON com pass; log com cardNumber/gatewayKey
// Depois: const { pass, ...safe } = user; res.json(safe);  // e remover os console.log de segredo
```
> O harness tolera essa remoção de campo (shape frouxo); a classe de status não muda.

---

## 11. Efeito no import → composition root / app factory
**Princípio:** inicialização é explícita no entry point, não no carregamento do módulo.

```python
# Antes (Flask): db.create_all() no topo do módulo; get_db() conecta no import
# Depois (app.py)
def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)
    db.init_app(app)
    register_routes(app); register_error_handler(app)
    return app
# schema criado por um comando/CLI explícito, não no import
```
```js
// Antes (Express): initDb() roda ao require do módulo
// Depois: app.js chama manager.initDb() explicitamente antes de listen()
```
