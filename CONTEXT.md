# Contexto: Auditoria & Refatoração Arquitetural

Glossário (linguagem ubíqua) do domínio desta skill: auditar uma codebase
legada, classificar problemas e refatorá-la para o padrão MVC. Os termos abaixo
são do domínio **da skill** — não do negócio dos projetos-alvo (e-commerce, LMS,
task manager), que são vocabulário de cada projeto, não deste.

## Severidade

Escala de classificação de cada achado, baseada em violações de MVC/SOLID e
segurança. É a régua canônica da auditoria — não inventar níveis paralelos.

**CRITICAL**:
Falha grave de arquitetura ou segurança que impede o funcionamento correto, expõe
dados sensíveis (ex: credencial hardcoded, SQL Injection) ou viola completamente a
separação de responsabilidades (ex: God Class com banco, lógica e roteamento juntos).

**HIGH**:
Violação forte de MVC/SOLID que dificulta muito manutenção e teste (ex: lógica de
negócio pesada presa em Controller, acoplamento forte sem injeção de dependência,
estado global mutável).

**MEDIUM**:
Padronização, duplicação ou gargalo moderado de performance (ex: query N+1,
middleware mal usado, validação ausente em rota).

**LOW**:
Legibilidade, nomenclatura ruim ou _magic numbers_ soltos.

## Achado

**Achado** (_finding_):
Uma ocorrência concreta de um anti-pattern num arquivo e linha exatos, com
severidade, descrição, impacto e recomendação. É a unidade do relatório de auditoria.
_Avoid_: problema, issue, bug, ocorrência

**Anti-pattern**:
Padrão recorrente e nomeado de design ruim que a skill sabe detectar (ex: God Class,
SQL Injection por concatenação). Vive no **catálogo**.
_Avoid_: má prática, erro

**Code smell**:
Sinal mais sutil de que algo está errado, sem ser necessariamente um anti-pattern
fechado (ex: método longo, nome ruim). Geralmente LOW/MEDIUM.
_Avoid_: cheiro de código

**API deprecated**:
Uso de API obsoleta cujo equivalente moderno é recomendado (ex: `datetime.utcnow()`).
Categoria de detecção obrigatória no catálogo.
_Avoid_: API velha, API legada

## Fases

**Análise** (Fase 1):
Detectar stack (linguagem, framework, banco), mapear a arquitetura atual e imprimir
um resumo. Não modifica nada.
_Avoid_: scan, varredura

**Auditoria** (Fase 2):
Cruzar o código contra o catálogo, gerar o relatório de achados ordenado por
severidade e **pausar pedindo confirmação** antes de qualquer mudança.
_Avoid_: revisão, review

**Refatoração** (Fase 3):
Reestruturar para MVC eliminando os achados e validar que a aplicação continua
funcionando.
_Avoid_: correção, fix, conserto

## Arquitetura-alvo

**Camada MVC**:
Uma das três responsabilidades-alvo. **Model** abstrai dados/persistência/domínio;
**View/Rotas** faz roteamento HTTP e serialização (sem lógica de negócio);
**Controller** orquestra o fluxo da requisição. _Service_ e _composition root_ apoiam.
_Avoid_: módulo, pacote (quando se quer dizer camada)

**Composition root** (_entry point_):
Ponto único onde a aplicação é montada (configuração, rotas, dependências) e sobe.
_Avoid_: main, bootstrap (quando se quer dizer o ponto de composição)

## Conhecimento da skill

**Catálogo**:
Arquivo de referência com os anti-patterns conhecidos, cada um com sinais de
detecção e severidade.
_Avoid_: lista de problemas

**Playbook**:
Arquivo de referência com transformações concretas (antes/depois) para corrigir
cada anti-pattern.
_Avoid_: receitas, guia de correção

**Harness de caracterização** (_smoke_):
Baseline gerado pela skill que sobe o app e bate em todos os endpoints, gravando
status e shape **antes** da refatoração; re-rodado **depois** para provar que o
contrato não quebrou. É o gate de validação e a peça "teste que falha primeiro" do TDD.
_Avoid_: teste de fumaça, suíte, e2e

**Stack**:
A combinação linguagem + framework + banco de um projeto-alvo (ex: Python/Flask/SQLite).
A skill é **agnóstica de stack**: o mesmo SKILL.md funciona nas três.
_Avoid_: tecnologia, plataforma
