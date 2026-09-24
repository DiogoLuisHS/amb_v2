# 📜 Changelog — AMB_V2

Todas as alterações notáveis, novas funcionalidades, refatorações e correções de bugs deste projeto estão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [2.4.1] — 2026-09-23

### 🤖 Agentes, Regras & Governança Cognitiva (/learn)
- **Nova Skill Mestre (`amb-master-ecosystem`):** Referência completa e unificada da CLI `amb`, matriz de comandos, cheatsheet de troubleshooting e desenvolvimento por lote de prompts (`-p`).
- **Atualização Canônica das 7 Skills Especialistas:** Alinhamento de todos os caminhos para a arquitetura modular `amb_cli/` e documentação de novos recursos (`amb gui`, auto-draft PR com `gh pr ready`, `amb config --gemini-confirm`, SRP prompts no pipeline).
- **Alinhamento das Regras Arquiteturais:** Atualização das referências de bootstrap, exceções e camadas em `.agents/rules/` (`01_single_responsibility.md`, `03_dry_and_zero_redundancy.md`, `04_code_quality_and_typing.md`).
- **159 Testes Unitários Verificados:** Integridade mantida com 100% de sucesso.

---

## [2.4.0] — 2026-09-18

### 🏗️ Arquitetura & Refatoração (Segregação Core vs Workspace)
- **Desacoplamento Total de Configurações:** Separação estrita entre a infraestrutura interna do Framework AMB (`amb_cli/core/`) e as configurações do projeto consumidor (`amb_cli/workspace/`).
- **Eliminação de Módulos Facade Obsoletos:** Remoção completa da pasta legada `amb_cli/config/` e de todos os arquivos temporários de retrocompatibilidade ("Facade Module").
- **Novo Pacote `amb_cli/core/` (Infraestrutura AMB):**
  - `bootstrap.py`: Gestão de `sys.path` e canônicos subdiretórios.
  - `logger.py`: Logging padronizado e cores ANSI (`Colors`).
  - `exceptions.py`: Hierarquia de exceções (`AmbError`, `ConfigurationError`, `ApiExecutionError`).
  - `env.py`: Resolução segura e tipada de variáveis de ambiente.
  - `diagnostics.py`: Diagnóstico de saúde e credenciais do ambiente (`amb check`).
- **Novo Pacote `amb_cli/workspace/` (Projeto Consumidor Alvo):**
  - `project_context.py`: Identificação da raiz do repositório, metadados (`amb_project.json`) e dispositivo.
  - `rules_manager.py`: Governança e injeção de regras arquiteturais (`.agents/rules/`).
  - `design_tokens.py`: Extração e parser de tokens visuais.
  - `setup/`: Subpacote contendo analisador de stack (`project_analyzer.py`), provisionador de ambiente (`amb_provisioner.py`), sintetizador cognitivo (`cognitive_synthesizer.py`) e orquestrador (`setup_project.py`).
- **Migração Global de Imports:** 100% dos arquivos do pacote `amb_cli/` e da suíte `tests/` atualizados para referenciar diretamente `core` e `workspace`.
- **158 Testes Unitários Verificados:** Todos os testes passando com 100% de sucesso.

---

## [2.3.0] — 2026-09-18

### ✨ Adicionado
- **Arquitetura 100% Atômica (Regra 02):** Todos os 92 arquivos da biblioteca `amb_cli/` foram refatorados para ficarem estritamente abaixo do teto de 300 linhas por arquivo.
- **Novos Subpacotes Especializados (`_core`):**
  - `amb_cli/agents/auto_reply_core/`: Extração de histórico turn-by-turn (`turn_extractor`), consultor cognitivo (`cognitive_advisor`) e despacho de feedback (`feedback_dispatcher`).
  - `amb_cli/agents/loop_core/`: Despachante de ciclos (`cycle_dispatcher`) e assistente de sessão (`session_assistant`).
  - `amb_cli/architecture/context_core/`: Constantes e configurações de camadas de dependência.
  - `amb_cli/cli_modules/handlers_core/`: Handlers modulares isolados por domínio (`antigravity_handler`, `git_handler`, `jules_handler`, `stitch_handler`).
  - `amb_cli/config/config_core/`: Diagnóstico de ambiente e extração de tokens de design.
  - `amb_cli/config/setup_modules/`: Analisador de projetos, provisionador `.amb/` e sintetizador cognitivo de personas.
  - `amb_cli/gui/wizard_core/`: Runner dinâmico de comandos (`runner_tab`), gestor de `.env` (`settings_tab`) e extrator de árvore de comandos (`parser_extractor`).
  - `amb_cli/pipeline/pipeline_core/`: Estágio visual de design (`design_stage`) e construtor de prompts especializados (`prompt_builder`).
  - `amb_cli/integrations/jules/jules_core/`: Helpers e normalizadores de rotas do Google Jules.
  - `amb_cli/integrations/stitch/stitch_core/`: Sincronização de design tokens, gerenciador de telas e assets.
  - `amb_cli/integrations/git/git_core/`: Automação da GitHub CLI (`gh`).
  - `amb_cli/integrations/antigravity/antigravity_core/`: Backend REST para a API Gemini.
- **Governança Centralizada de Regras (`RulesManager`):** Módulo centralizado em `amb_cli/config/rules_manager.py` com resolução prioritária de diretórios (`.agents/rules/`), fechamento seguro de fences markdown e cache em memória.
- **Gatekeeper Local de Qualidade (`QualityGatekeeper`):** Módulo centralizado em `amb_cli/pipeline/quality_gatekeeper.py` com detecção automática de stacks (Node.js, Python, Go) e execução de testes pré/pós-merge.
- **Suíte de Testes Automatizados Expandida:** Aumento de 62 para **158 testes unitários** (100% green), cobrindo todos os módulos refatorados, parsers e comandos da CLI.
- **Nova Suíte de Testes da CLI (`tests/test_cli_commands.py`):** 14 testes cobrindo todos os comandos principais, subcomandos, argumentos opcionais e delegações de handlers.
- **Comando `amb config`:** Adicionado para inspecionar e alternar a exigência de confirmação manual em chamadas ao Gemini (`amb config --gemini-confirm on/off`).
- **Suporte a Novas Flags da CLI:**
  - `amb agent`: Adicionadas flags `--modules <m1,m2>` (rotação de módulos por ciclo) e `--no-auto-merge` (desativação de merge automático).
  - `amb prompt`: Adicionada flag `--output` / `-o` para salvar o prompt sintetizado diretamente em arquivo.
  - `amb validate`: Adicionada flag `--json` para emissão do relatório em formato estruturado.

### 🔄 Modificado
- **Simplificação e Desduplicação de Comandos da CLI:**
  - `amb advisor` simplificado para delegar diretamente ao handler especializado do Jules (`handle_cmd_jules` com `jules_cmd = "reply"`).
  - `amb validate` simplificado para delegar diretamente ao handler do Antigravity (`handle_cmd_antigravity` com `agy_cmd = "validate"`).
  - `amb prompt --synthesize` unificado para utilizar o pipeline de síntese do Antigravity.
- **Bootstrap Canônico Centralizado:** Sincronização de `CANONICAL_SUBMODULES` em `amb_cli/config/bootstrap.py` para garantir resolução determinística de `sys.path` tanto no repositório `amb_v2` quanto em projetos consumidores externos.
- **Documentação Unificada no `README.md`:** Seções 2.7 (Antigravity) e 2.8 (Git) adicionadas, Tabela 3 de Referência Rápida sincronizada com todos os comandos e estrutura do repositório atualizada.
- **Smoke Test da Raiz (`test_check.py`):** Atualizado para utilizar `amb_bootstrap`, garantindo verificação instantânea da saúde do ambiente e dos imports.

### 🐛 Corrigido
- **Prevenção de Respostas Consecutivas Duplicadas:** Correção no `auto_reply.py` e `autonomous_loop.py` para rastrear o último turno de conversa (`is_awaiting_user_action`) e impedir o envio de sugestões quando a última mensagem já tiver sido enviada pelo usuário.
- **Normalização Universal de Sessões Jules:** `JulesClient.normalize_session_id` agora aceita IDs numéricos puros, rotas de API (`sessions/<id>`) e URLs completas do console web (`https://jules.google.com/session/...`).
- **Publicação Automática de PRs em Draft:** `amb jules merge` e o loop autônomo executam `gh pr ready` automaticamente antes do merge, eliminando travamentos causados pelo padrão Draft da API do Jules.
- **Detecção de Headers Markdown em Regras:** Correção no parser de regras do `auto_reply` para reconhecer headers em qualquer nível (`#`, `##`, `###`), evitando vazamento de diretrizes de commit para o prompt do Jules.
- **Alerta de Sessões `COMPLETED`:** O monitor de sessões agora identifica sessões concluídas cujo PR ainda não foi integrado e sugere a execução do merge.
- **Parsing Polimórfico de Respostas do Jules:** Tratamento seguro para respostas retornadas como lista direta ou dicionário com chave `"activities"`.
- **Truncamento Seguro de Saídas de Bash:** Expansão de 150 para 800 caracteres com indicador claro de corte para melhor contexto em falhas de build/testes enviadas ao Gemini.
- **Detecção de Branch Padrão:** Substituição da branch fixa `develop` pela detecção automática da branch ativa do repositório local (`git branch --show-current`).

---

## [2.2.0] — 2026-09-10

### ✨ Adicionado
- **Loop Contínuo de Engenharia Autônoma (`amb agent --loop`):** Orquestração ponta a ponta envolvendo despacho de tarefas para Cloud VMs do Jules, auto-resposta com Gemini e auto-merge no Git após aprovação de testes.
- **Sistema de Personas Dinâmicas:** Suporte à descoberta e execução de personas em markdown a partir da pasta `.amb/personas/` (ex: `engineer.md`).
- **Integração com Google Stitch SDK:** Suporte à geração, refinamento, variantes e download de telas e assets via Node.js runner e cliente Python.
- **Integração Cognitiva com Google Antigravity & Gemini:** Síntese de requisitos informais em prompts estruturados e auditoria estática contra regras do repositório.
- **Assistente Gráfico Nativo (Tkinter UI):** Interface visual `amb gui` para construção dinâmica de comandos e gestão de variáveis do `.env`.

### 🔄 Modificado
- Reformulação da CLI unificada sob o comando global `amb`.
- Diagnóstico completo de credenciais e dependências via `amb check`.

---

## [2.1.0] — 2026-08-28

### ✨ Adicionado
- **Cliente REST do Google Jules:** Suporte a listagem, detalhes, criação de sessões, aprovação de planos e envio de mensagens.
- **Comando `amb setup`:** Assistente interativo para análise de stack do repositório, configuração de comandos de QA e provisionamento da estrutura `.amb/`.
- **Mapeamento Arquitetural por Camadas (`amb context`):** Geração de roteiros ordenados de arquivos (Database ➔ Services ➔ API ➔ UI) para consumo por modelos de IA.
- **Leitor de Schemas Drizzle/SQL (`amb schema`):** Inspeção read-only de tabelas e colunas para suporte a prompts de engenharia.

---

## [2.0.0] — 2026-08-15

### ✨ Adicionado
- **Lançamento Inicial do AMB_V2:** Fundação do ecossistema de automação de engenharia para monorepos e projetos modernos.
- Arquitetura de configuração centralizada via arquivo `.env`.
- Suporte a empacotamento global via `pip install -e .`.
