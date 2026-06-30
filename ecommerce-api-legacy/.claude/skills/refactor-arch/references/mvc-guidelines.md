# Guidelines da arquitetura MVC alvo

A Fase 3 reestrutura para estas camadas. Regra-mãe: **cada camada tem uma responsabilidade; dependências apontam para dentro** (rota → controller → model). Nada de pular camada nem inverter a seta.

## Camadas

### Model (`models/`)
Abstrai dados, persistência e regras de domínio puras. É a **única** camada que fala com o banco.
- Uma entidade/agregado por arquivo (`produto_model.py`, `user.model.js`).
- Expõe operações de domínio (`buscar_por_id`, `criar`, `login`), não SQL solto pelos handlers.
- Sem `request`/`response` aqui — Model não conhece HTTP.

### View / Rotas (`views/` ou `routes/`)
Roteamento HTTP e serialização. **Sem lógica de negócio.**
- Mapeia `MÉTODO /path` → método do controller.
- Faz parse de input e formatação de output (status + corpo). Decisões de negócio ficam no controller.

### Controller (`controllers/`)
Orquestra o fluxo da requisição: valida input, chama models/services, monta a resposta.
- Um controller por recurso (`produto_controller`, `pedido_controller`).
- Não acessa o banco direto (vai pelo Model) nem dispara efeito externo direto (vai por um Service).

### Service (`services/`) — quando houver lógica/efeito que não é de um único model
Casos de uso que cruzam models ou tocam o mundo externo (e-mail, pagamento, cache). Mantém o controller fino e o efeito isolado (e testável/stubável).

### Config (`config/`)
Configuração e segredos **fora do código**, lidos do ambiente (`os.environ` / `process.env`), com defaults seguros. Zero credencial hardcoded. `DEBUG` vem de env, default desligado.

### Tratamento de erro centralizado
Um único ponto que captura exceções e devolve resposta padronizada (Flask `@app.errorhandler` / middleware de erro do Express). Handlers param de repetir `try/except → str(e)`; o cliente nunca recebe detalhe interno.

### Entry point / composition root
Um arquivo onde a aplicação é montada: cria o app, carrega config, registra rotas e o handler de erro, conecta dependências e sobe. Sem efeito colateral em tempo de import (criação de schema, conexão viva) — inicialização é explícita.

## Estrutura alvo (exemplo)

```
src/
├── config/settings.py          # config + segredos do ambiente
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/routes.py             # ou routes/ por recurso
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── services/notification_service.py
├── middlewares/error_handler.py
└── app.py                      # composition root
```

## Adaptação ao ponto de partida

- **Monólito** (tudo em poucos arquivos): crie as camadas do zero e mova cada responsabilidade.
- **Parcialmente organizado** (já tem `models/`, `routes/`, `services/`): não recrie o que existe — **corrija os vazamentos** (lógica na rota → controller/service; segredo no código → config; model que vaza campo sensível → serializer; efeito no import → composition root). Melhorar a estrutura existente conta como Fase 3.

A regra de ouro do contrato: refatorar **preserva o comportamento externo** (a classe de status de cada endpoint), removendo só o que é inseguro (segredo/PII no corpo). É isso que o harness verde prova.
