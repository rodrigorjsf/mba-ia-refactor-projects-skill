================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project (API da Loja)
Stack:   Python 3.14 + Flask 3.1.1 + SQLite (sqlite3 cru, sem ORM)
Files:   4 analyzed (app.py, controllers.py, models.py, database.py) | ~783 lines of code

## Summary
CRITICAL: 5 | HIGH: 4 | MEDIUM: 4 | LOW: 4

> Catálogo cruzado por completo, incluindo a seção de **APIs deprecated**: não há
> `datetime.utcnow()`, `hashlib.md5/sha1`, `datetime.strptime`, `body-parser`,
> `var`/callbacks aninhados nem callback do `sqlite3` (Node) neste código — os
> timestamps são `CURRENT_TIMESTAMP` no SQL. A única modernização de API
> aplicável (senha sem hash → `werkzeug.security`) está absorvida no achado
> CRITICAL de senha em texto plano abaixo.

## Findings

### [CRITICAL] SQL Injection por concatenação de string
File: models.py:28, 47-50, 57-61, 68, 92, 109-111, 126-129, 140, 148-151, 155-166, 174, 188, 192, 220, 224, 280, 289-297
Description: Praticamente toda query é montada concatenando input do usuário direto na string SQL — ex. `cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))` (linha 28), o `INSERT` de produtos interpolando `nome`/`descricao`/`categoria` (47-50), o login `"... WHERE email = '" + email + "' AND senha = '" + senha + "'"` (109-111) e a busca dinâmica com `LIKE '%" + termo + "%'` (291). Nenhum placeholder parametrizado é usado nos handlers.
Impact: Injeção de SQL trivial — leitura/escrita arbitrária no banco, bypass de login (`' OR '1'='1`), e dump completo de usuários/senhas. Comprometimento total da base.
Recommendation: Trocar 100% das queries por placeholders `?` com tupla de parâmetros (playbook §1). A camada Model passa a ser a única a falar SQL, sempre parametrizado.

### [CRITICAL] Endpoint de SQL arbitrário e operação destrutiva sem auth
File: app.py:59-78 (`POST /admin/query`), app.py:47-57 (`POST /admin/reset-db`)
Description: `/admin/query` repassa o corpo `dados["sql"]` direto para `cursor.execute(query)` (linha 69), executando qualquer SQL do request. `/admin/reset-db` faz `DELETE FROM` em todas as tabelas (51-54). Ambos sem nenhuma autenticação/autorização.
Impact: Equivalente a RCE no banco e perda total de dados por qualquer cliente anônimo. É o anti-pattern mais grave do catálogo.
Recommendation: `/admin/query` (SQL arbitrário) **removido** — não há forma segura desse endpoint; agora retorna 404. `/admin/reset-db` agora exige header `X-Admin-Token` (env `ADMIN_TOKEN`); sem ele, 401, sem tocar no banco. São mudanças **intencionais** de classe de status (200→404/401): o `harness/baseline.json` foi re-baselinado para esses dois endpoints e a mudança está documentada na seção "Fase 3 — resultado" abaixo (ver `mvc-guidelines.md` › _exceção ao harness verde_). Princípio: endereçar o achado vence o contrato — nunca manter um endpoint inseguro aberto só para o status bater.

### [CRITICAL] Credenciais / segredos hardcoded no código
File: app.py:7 (`app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"`)
Description: A `SECRET_KEY` da aplicação é um literal no código-fonte, versionado no repositório.
Impact: Sessões/tokens forjáveis por qualquer um com acesso ao repo; o segredo não pode ser rotacionado sem deploy de código.
Recommendation: Mover para `config/settings.py` lido de `os.environ`, com default seguro só para dev (playbook §3). Zero credencial hardcoded.

### [CRITICAL] Senha armazenada e comparada em texto plano
File: database.py:75-83 (seed), models.py:126-129 (`criar_usuario`), models.py:105-120 (`login_usuario`)
Description: O seed grava senhas em claro (`"admin123"`, `"123456"`, `"senha123"`); `criar_usuario` insere a senha crua; `login_usuario` compara a senha plana dentro do `WHERE ... AND senha = '...'`. Nenhum hash é aplicado.
Impact: Um vazamento do banco expõe todas as senhas em claro; combinado com a SQLi acima, comprometimento imediato de todas as contas.
Recommendation: Usar `werkzeug.security.generate_password_hash`/`check_password_hash` (já vem com Flask) no cadastro e no login (playbook §4). **Migrar os usuários semeados** para o hash, senão o `/login` regride 200→401 e o harness fica vermelho.

### [CRITICAL] Dado sensível exposto na resposta HTTP
File: controllers.py:288-289 (`/health` devolve `debug` e `secret_key`), models.py:83 e 99 (serialização de usuário inclui `senha`)
Description: O `/health` retorna `"debug": True` e `"secret_key": "minha-chave-super-secreta-123"` no corpo JSON. As funções `get_todos_usuarios` (linha 83) e `get_usuario_por_id` (linha 99) incluem o campo `senha` no dict serializado, então `GET /usuarios` e `GET /usuarios/<id>` vazam a senha.
Impact: Vazamento direto da secret key e das senhas dos usuários por endpoints de leitura comuns.
Recommendation: Serializador que omite segredo/PII (playbook §10): `/health` devolve só `status`/`counts`; a serialização de usuário nunca inclui `senha`. O harness tolera a remoção desses campos (shape frouxo), a classe de status não muda.

### [HIGH] God Module (persistência + negócio + formatação de 4 domínios)
File: models.py:1-315 (produtos, usuários, pedidos/itens e relatórios num só arquivo); controllers.py:1-293 (todos os handlers de todos os recursos juntos)
Description: `models.py` concentra SQL, regras de negócio (cálculo de total de pedido, faixas de desconto do relatório) e formatação de quatro domínios. `controllers.py` faz o mesmo do lado dos handlers. Nenhuma fronteira por recurso.
Impact: Impossível testar/alterar um domínio em isolamento; qualquer mudança arrisca os demais.
Recommendation: Separar por recurso em `models/` (produto/usuario/pedido/relatorio) e `controllers/` (playbook §2), seguindo `mvc-guidelines.md`.

### [HIGH] Lógica de negócio / efeito colateral no controller
File: controllers.py:208-210 (`print("ENVIANDO EMAIL...")`, SMS, PUSH em `criar_pedido`), controllers.py:247-250 (notificações em `atualizar_status_pedido`)
Description: O handler de pedido dispara "efeitos externos" (e-mail/SMS/push, hoje como `print`) e o de status emite notificações — efeito de negócio preso ao HTTP, dentro do controller.
Impact: Acoplamento, efeito não-testável/stubável, duplicação de fluxo.
Recommendation: Extrair para um `NotificationService` isolado e chamável pelo controller (playbook §5); o controller só orquestra.

### [HIGH] Debug mode ligado (default ligado, não vem do ambiente)
File: app.py:8 (`app.config["DEBUG"] = True`), app.py:88 (`app.run(..., debug=True)`)
Description: Debug está hard-ligado no código, não condicionado a variável de ambiente.
Impact: O debugger interativo do Werkzeug executa código arbitrário e vaza stack/estado interno se exposto.
Recommendation: `DEBUG` vem de `config/settings.py` lido do ambiente, default desligado (playbook §9).

### [HIGH] Estado global mutável (conexão de banco em nível de módulo)
File: database.py:4 (`db_connection = None`), reusado por `get_db()` (database.py:7-12) com `check_same_thread=False`
Description: Uma única conexão SQLite global é criada uma vez e reusada por todos os requests/threads.
Impact: Corrida entre requests, cursores compartilhados, vazamento de estado, teste impossível.
Recommendation: Conexão por request (ex. `flask.g` + `teardown_appcontext`) e inicialização explícita; remover o global mutável (mvc-guidelines: composition root; playbook §11).

### [MEDIUM] Query N+1 na montagem de pedidos
File: models.py:187-199 (`get_pedidos_usuario`), models.py:219-231 (`get_todos_pedidos`)
Description: Para cada pedido abre-se um cursor para os itens e, para cada item, mais um `SELECT nome FROM produtos WHERE id = ...` — cursores aninhados em três níveis.
Impact: Latência cresce linearmente com pedidos×itens; gargalo sob carga.
Recommendation: Uma query com `JOIN` entre `pedidos`/`itens_pedido`/`produtos` e agrupamento em memória (playbook §7).

### [MEDIUM] Tratamento de erro vazando detalhe interno (duplicado por handler)
File: controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292; app.py:77-78
Description: Quase todo handler repete `except Exception as e: return jsonify({"erro": str(e)}), 500`, devolvendo a mensagem interna da exceção ao cliente.
Impact: Vaza estrutura interna/stack, mascara bugs e duplica o mesmo bloco ~17 vezes.
Recommendation: `@app.errorhandler(Exception)` central que loga e devolve `{"erro": "Erro interno"}` 500 sem `str(e)` (playbook §8); handlers param de repetir try/except.

### [MEDIUM] Falta de integridade referencial no delete
File: models.py:65-70 (`deletar_produto` → `DELETE FROM produtos WHERE id = ...`)
Description: Apagar um produto não trata `itens_pedido` que o referenciam — deixa itens órfãos apontando para produto inexistente.
Impact: Dados órfãos, relatórios e listagens de pedido inconsistentes (`produto_nome` vira "Desconhecido").
Recommendation: Apagar dependentes em transação (cascade) ou bloquear o delete quando houver itens vinculados.

### [MEDIUM] Validação de input duplicada inline no handler
File: controllers.py:28-54 (`criar_produto`) vs controllers.py:72-90 (`atualizar_produto`)
Description: O mesmo bloco de validação (`if not dados`, `if "nome" not in dados`, `preco < 0`, `estoque < 0`, ...) é copiado entre criar e atualizar produto, dentro do handler.
Impact: Regras divergem entre endpoints (a checagem de categoria existe no create mas não no update); manutenção cara.
Recommendation: Centralizar a validação de produto num único ponto (schema/validador no controller ou service) reutilizado por create e update.

### [LOW] Log ad-hoc via `print`
File: controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250; app.py:56, 83-86
Description: Eventos e erros são logados com `print(...)` cru no stdout.
Impact: Sem nível, sem destino configurável, sem correlação; logs misturados ao stdout do servidor.
Recommendation: Usar `app.logger`/`logging` com nível; remover os `print` de evento (e principalmente os que concatenam dados sensíveis).

### [LOW] Magic numbers nas faixas de desconto
File: models.py:257-262 (`10000`, `5000`, `1000`, `0.1`, `0.05`, `0.02`)
Description: As faixas de faturamento e taxas de desconto do relatório são literais soltos no cálculo.
Impact: Intenção de negócio obscura; mudança arriscada e espalhada.
Recommendation: Extrair para constantes nomeadas (ex. `FAIXAS_DESCONTO`) no model/relatório.

### [LOW] Código duplicado entre listagens de pedido
File: models.py:171-201 (`get_pedidos_usuario`) ≈ models.py:203-233 (`get_todos_pedidos`)
Description: As duas funções são quase idênticas, diferindo só pelo filtro `WHERE usuario_id = ?` ausente na segunda.
Impact: Correção (ex. a do N+1) precisa ser feita em dois lugares.
Recommendation: Uma única função parametrizada pelo filtro opcional de usuário.

### [LOW] Nomes crípticos / shadowing de builtin
File: models.py:187/191/219/223 (`cursor2`, `cursor3`); `id` como parâmetro sombreando o builtin em models.py:24,43,54,65,89 e controllers.py:14,64,98
Description: Cursores numerados não-descritivos e o parâmetro `id` sombreando o builtin `id()` em várias funções.
Impact: Legibilidade ruim e risco de erro sutil.
Recommendation: Nomear cursores pelo papel (`cursor_itens`, `cursor_produto`) e renomear o parâmetro (`produto_id`/`usuario_id`).

================================
Total: 17 findings
================================

Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]
> s

================================
FASE 3 — RESULTADO
================================
Estrutura MVC criada: `config/settings.py` (sem segredo hardcoded), `models/`
(produto/usuario/pedido/relatorio), `views/routes.py` (só roteamento),
`controllers/` (1 por recurso), `services/notification_service.py`,
`middlewares/error_handler.py` (erro centralizado), `app.py` (composition root,
sem efeito no import). SQL 100% parametrizado; senha → `werkzeug.security` (scrypt)
com o seed migrado; `/health` e a serialização de usuário não vazam mais
segredo/senha.

Validação (harness de caracterização, 19 endpoints):
  ✓ App sobe sem erro (`python app.py`)
  ✓ 17 endpoints preservaram a classe de status (2xx → 2xx)
  ✓ `/health`: removidos `secret_key/debug/db_path/ambiente` (shape change tolerado)
  ✓ Mudanças intencionais de segurança (re-baselinadas, ver mvc-guidelines › exceção):
      - POST /admin/query   200 → 404  (endpoint de SQL arbitrário removido)
      - POST /admin/reset-db 200 → 401  (agora exige X-Admin-Token)
  ✓ GREEN — nenhuma regressão acidental de classe de status
================================
