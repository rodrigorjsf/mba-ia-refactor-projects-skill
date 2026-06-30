---
name: refactor-arch
description: Audita e refatora um projeto para a arquitetura MVC, agnóstica de stack. Use quando o usuário pedir para auditar ou refatorar a arquitetura de um projeto, detectar anti-patterns e code smells por severidade, ou invocar /refactor-arch dentro de um projeto.
---

# refactor-arch — auditoria e refatoração arquitetural para MVC

Roda **três fases sequenciais** sobre o projeto onde é invocada: **Análise → Auditoria → Refatoração**. Agnóstica de stack — a Fase 1 detecta linguagem/framework/banco e tudo a seguir se adapta. Duas leis invioláveis:

1. **Nunca pule a confirmação.** A Fase 2 termina pedindo autorização humana; só a Fase 3 toca arquivos-fonte.
2. **Nunca aceite refatoração sem o harness verde.** O baseline capturado na Fase 1 é o contrato; a Fase 3 só conclui se o harness re-rodar **verde**.

## Conhecimento (reference files)

Carregue cada um ao chegar na fase correspondente:

- `references/analysis.md` — heurísticas de detecção de stack e mapeamento de arquitetura (Fase 1)
- `references/anti-patterns.md` — catálogo de anti-patterns + APIs deprecated (Fase 2)
- `references/report-template.md` — formato do relatório de auditoria (Fase 2)
- `references/mvc-guidelines.md` — responsabilidades de cada camada MVC alvo (Fase 3)
- `references/playbook.md` — transformações antes/depois por anti-pattern (Fase 3)

## Fase 1 — Análise

1. Detecte a **stack** (linguagem, framework, banco) e o **domínio** do negócio pelas heurísticas de `references/analysis.md`.
2. Mapeie a arquitetura atual: arquivos-fonte, camadas existentes (ou a ausência delas) e o **route map** — todos os endpoints (método + path), lendo o registro de rotas e qualquer arquivo tipo `api.http`.
3. Imprima o resumo: linguagem, framework, dependências, domínio, arquitetura, nº de arquivos analisados, tabelas/coleções do banco.
4. Gere o **harness de caracterização** a partir do route map e capture o **baseline**:
   - Sobe o app num **porto livre**, em background; espera ficar pronto (poll no `/` ou `/health`, tratando qualquer resposta HTTP — incl. 404 — como "no ar"). Se o porto é hardcoded e o app não expõe objeto importável nem lê `PORT`, suba o **entry point como subprocess** num porto livre. Rode o harness a partir da **raiz do projeto** (ex: `PYTHONPATH=.`) para o import do app resolver. Se o schema não é criado no boot, inicialize-o no harness.
   - **Semeie dados representativos** antes de capturar (rode o seed do projeto ou crie o mínimo): tabelas vazias travam menos classes de status (login 200 vs 401, `GET /x/1` 200 vs 404) e enfraquecem o baseline como contrato.
   - Bate em cada endpoint: GET sem corpo; para POST/PUT/DELETE, um payload mínimo representativo inferido das validações do código (ou do `api.http`). Envie `Content-Type: application/json` nas requisições com corpo — sem o header, frameworks como Flask retornam 415, que o `try/except` original vira 500 e falsifica o baseline.
   - Grava por endpoint `{método, path, classe_de_status, chaves_de_topo}` em `harness/baseline.json` dentro do projeto, e o script gerador em `harness/`. Corpo **array**: registre as chaves do 1º elemento (ou `[]` se vazio); corpo **texto/escalar**: um sentinela (`<text>`). A classe de status é o gate; o shape é diff informativo.
   - Se algum endpoint exercitado dispara um **efeito externo real** (e-mail/SMS/cobrança), neutralize-o (stub/monkeypatch/variável de ambiente) **antes** de capturar. Só neutralize o que um endpoint do harness realmente alcança — não invente stub para código morto/não-roteado.

**Completo quando:** o resumo foi impresso E `harness/baseline.json` existe com todos os endpoints capturados (app sobe, nenhum 5xx inesperado no baseline).

## Fase 2 — Auditoria

1. Cruze o código contra **todo** o catálogo de `references/anti-patterns.md`, incluindo a seção de APIs deprecated.
2. Para cada ocorrência, registre um **achado**: arquivo:linha exatos, severidade (CRITICAL/HIGH/MEDIUM/LOW), descrição, impacto e recomendação.
3. Gere o relatório no formato de `references/report-template.md`, **ordenado por severidade decrescente** (CRITICAL → HIGH → MEDIUM → LOW), e salve em `reports/audit-project-<N>.md` (crie `reports/` se preciso).
4. **PARE.** Imprima o resumo de contagem por severidade e pergunte exatamente: `Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]`. Não toque em nenhum arquivo-fonte até um "sim" explícito; em "não", encerre sem alterar nada.

**Completo quando:** o relatório tem **≥5 achados** com **≥1 CRITICAL ou HIGH**, cada um com arquivo:linha, ordenados por severidade, salvo em `reports/`, E a skill pausou aguardando confirmação.

## Fase 3 — Refatoração

Só após "sim".

1. **Snapshot "antes":** capture a árvore de diretórios atual (`find`/`tree`) para o comparativo antes/depois.
2. Reestruture para o alvo MVC de `references/mvc-guidelines.md`, aplicando as transformações de `references/playbook.md` que casam com os achados: configuração sem segredo hardcoded, **Models** abstraindo dados, **Views/Rotas** sem lógica de negócio, **Controllers** orquestrando o fluxo, **tratamento de erro centralizado**, **entry point / composition root** claro.
3. **Regra do hash de senha:** ao trocar armazenamento de senha por hash, migre também os dados semeados (seed/fixtures) para o novo esquema — senão o login regride de 200→401 e o harness fica vermelho.
4. Re-rode o harness. **Verde** = para cada endpoint, a **classe de status** (2xx/4xx/5xx) é idêntica ao baseline. O shape do corpo é comparado de forma frouxa (chaves de topo): tolere campos removidos por segurança (ex: `senha`, `password`); trate qualquer **regressão de classe de status** como vermelho.
   - O diff de chaves-de-topo é **cego a campos aninhados**: se o segredo/PII está dentro de uma lista/objeto (ex: `dados[].senha`), o harness não enxerga a remoção — **verifique manualmente** que ele saiu.
   - O baseline com payload mínimo cobre o **caminho feliz**; ele não protege ramos 4xx/5xx. Quando viável, caracterize ao menos um ramo de erro por endpoint (GET inexistente → 404, corpo inválido → 400) para o gate pegar uma regressão tipo 404→500.
   - Correção que muda a classe de status **de propósito** (ex: pôr auth num endpoint destrutivo, remover endpoint de SQL arbitrário) é permitida: ver `references/mvc-guidelines.md` › _exceção ao harness verde_ (hardening + re-baseline + documentar). Nunca deixe um endpoint inseguro aberto só para o status bater.
5. Se vermelho (regressão acidental), conserte e re-rode até verde. Não declare pronto com o harness vermelho.

**Completo quando:** a estrutura MVC existe (config, models, views/rotas, controllers, erro centralizado, entry point), o app sobe sem erro, e o harness re-rodou **verde** (classe de status preservada em todos os endpoints).
