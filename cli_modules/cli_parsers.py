import argparse
from cli_modules.cli_handlers import (
    cmd_setup, cmd_prompt, cmd_check, cmd_monitor, cmd_advisor, cmd_dashboard,
    cmd_config, cmd_agent, cmd_jules, cmd_stitch, cmd_render, cmd_validate,
    cmd_pipeline, cmd_schema, cmd_context
)

def create_parser():
    parser = argparse.ArgumentParser(
        prog="amb",
        description="CLI Unificada do AMB_V2 — Automação, Agentes e Integrações para Monorepos e Projetos."
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # 1. amb setup
    p_setup = subparsers.add_parser("setup", aliases=["init"], help="Analisa e configura o projeto atual.")
    p_setup.add_argument("--auto", action="store_true", help="Executa o setup de forma automática/não-interativa.")
    p_setup.add_argument("--prompt", "-p", action="store_true", help="Exibe o Prompt Mestre de Auto-Configuração para colar em IAs.")
    p_setup.set_defaults(func=cmd_setup)

    # 1.1 amb prompt
    p_prompt = subparsers.add_parser("prompt", help="Exibe ou sintetiza com IA o Prompt de Desenvolvimento.")
    p_prompt.add_argument("--synthesize", "-s", help="Ideia informal a ser sintetizada em prompt estruturado com IA.")
    p_prompt.add_argument("--role", "-r", default="general", help="Especialidade para sintetização do prompt.")
    p_prompt.set_defaults(func=cmd_prompt)

    # 2. amb check
    p_check = subparsers.add_parser("check", aliases=["status"], help="Valida chaves e configurações do projeto ativo.")
    p_check.set_defaults(func=cmd_check)

    # 2.1 amb config
    p_cfg = subparsers.add_parser("config", aliases=["settings", "pref"], help="Configura preferências de IA, quotas e autorizações do AMB_V2.")
    p_cfg.add_argument("--gemini-confirm", choices=["on", "off", "true", "false"], help="Ativa (on) ou desativa (off) a exigência de autorização manual a cada chamada ao Gemini.")
    p_cfg.set_defaults(func=cmd_config)


    # 3. amb monitor
    p_mon = subparsers.add_parser("monitor", aliases=["watch", "sentinel"], help="Sentinela em tempo real (Jules + Render) com suporte a auto-resposta Gemini.")
    p_mon.add_argument("--interactive", "-i", action="store_true", help="Abre o menu interativo cognitivo (Advisor) para inspecionar e responder pendências.")
    p_mon.add_argument("--auto-approve", "-y", action="store_true", help="Aprova e responde chats automaticamente via Gemini.")
    p_mon.add_argument("--check-once", "-1", action="store_true", help="Executa apenas uma rodada de checagem e encerra.")
    p_mon.add_argument("--interval", type=int, default=15, help="Intervalo de polling em segundos (padrão: 15s).")
    p_mon.set_defaults(func=cmd_monitor)

    # 4. amb advisor
    p_adv = subparsers.add_parser("advisor", aliases=["ask"], help="Menu cognitivo para tirar dúvidas pendentes do Jules com IA.")
    p_adv.add_argument("--auto-approve", "-y", action="store_true", help="Responde todas as sessões pendentes em lote.")
    p_adv.set_defaults(func=cmd_advisor)

    # 5. amb dashboard (web SPA)
    p_dash = subparsers.add_parser("dashboard", aliases=["web", "ui"], help="Inicia o servidor e SPA do Dashboard Web em tempo real.")
    p_dash.add_argument("--port", "-p", type=int, default=3333, help="Porta HTTP do servidor (padrão: 3333).")
    p_dash.set_defaults(func=cmd_dashboard)

    # 6. amb agent
    p_agent = subparsers.add_parser("agent", aliases=["persona"], help="Executor de personas autônomas de manutenção.")
    p_agent.add_argument("--role", "-r", help="Nome da persona (ex: deadwood, beacon, bolt, align, etc.).")
    p_agent.add_argument("--all", "-a", action="store_true", help="Executa todas as personas em lote.")
    p_agent.add_argument("--task", "-t", help="Instruções ou escopo adicional.")
    p_agent.add_argument("--list", "-l", action="store_true", help="Lista todas as personas disponíveis.")
    p_agent.add_argument("--dispatch-jules", "-j", action="store_true", help="Despacha para o Google Jules na nuvem.")
    p_agent.add_argument("--loop", "-c", "--continuous", action="store_true", help="Executa o ciclo contínuo e autônomo de personas.")
    p_agent.add_argument("--max-cycles", type=int, help="Limite de ciclos no modo loop (se omitido, roda continuamente).")
    p_agent.add_argument("--branch", "-b", help="Branch de início para o Jules (se omitido, auto-detecta a branch ativa do Git).")
    p_agent.add_argument("--personas-dir", help="Pasta customizada de personas.")
    p_agent.set_defaults(func=cmd_agent)


    # 7. amb jules
    p_jules = subparsers.add_parser("jules", help="Comandos de integração com o Google Jules.")
    j_subs = p_jules.add_subparsers(dest="jules_cmd", help="Subcomandos do Jules")

    j_list = j_subs.add_parser("list", help="Lista sessões recentes.")
    j_list.add_argument("--limit", "-n", type=int, default=10, help="Limite de sessões.")

    j_get = j_subs.add_parser("get", help="Exibe detalhes, PR ou faz streaming ao vivo da sessão.")
    j_get.add_argument("session_id", help="ID da sessão.")
    j_get.add_argument("--watch", "-w", action="store_true", help="Acompanha em tempo real as atividades e saídas da sessão.")
    j_get.add_argument("--json", action="store_true", help="Saída em JSON puro.")

    j_create = j_subs.add_parser("create", help="Cria uma nova sessão no Jules.")
    j_create.add_argument("--prompt", "-p", required=True, help="Prompt da tarefa.")
    j_create.add_argument("--title", "-t", help="Título da sessão.")

    j_reply = j_subs.add_parser("reply", aliases=["advisor", "ask"], help="Responde uma dúvida com IA (ou envia mensagem direta se --message).")
    j_reply.add_argument("--session-id", "-s", required=False, help="ID da sessão (opcional; se omitido, lista todas as sessões pendentes).")
    j_reply.add_argument("--message", "-m", help="Mensagem direta manual a ser enviada ao chat.")
    j_reply.add_argument("--auto-approve", "-y", action="store_true", help="Envia resposta gerada pelo Gemini sem pedir confirmação.")

    j_app = j_subs.add_parser("approve", help="Aprova o plano de uma sessão.")
    j_app.add_argument("--session-id", "-s", required=True, help="ID da sessão.")

    j_merge = j_subs.add_parser("merge", help="Detecta o PR da sessão, aprova, faz merge no GitHub e valida localmente.")
    j_merge.add_argument("--session-id", "-s", help="ID da sessão para detectar o PR.")
    j_merge.add_argument("--auto-latest", action="store_true", help="Detecta automaticamente o PR aberto mais recente.")

    j_clean = j_subs.add_parser("clean", aliases=["cleanup"], help="Audita e remove na nuvem sessões do Jules já integradas.")
    j_clean.add_argument("--force", "-f", action="store_true", help="Remove sem pedir confirmação.")
    j_clean.add_argument("--failed", action="store_true", help="Remove todas as sessões que estão em estado de falha (FAILED).")
    p_jules.set_defaults(func=cmd_jules)

    # 8. amb stitch
    p_stitch = subparsers.add_parser("stitch", help="Comandos de integração com o Google Stitch SDK.")
    s_subs = p_stitch.add_subparsers(dest="stitch_cmd", help="Subcomandos do Stitch")

    s_gen = s_subs.add_parser("generate", help="Gera uma nova tela via Stitch.")
    s_gen.add_argument("--prompt", "-p", required=True, help="Descrição visual da tela.")
    s_gen.add_argument("--title", "-t", help="Título da tela.")

    s_ref = s_subs.add_parser("refine", help="Refina uma tela existente no Stitch com novas instruções.")
    s_ref.add_argument("--screen-id", "-s", required=True, help="ID da tela.")
    s_ref.add_argument("--prompt", "-p", required=True, help="Instruções de edição e refinamento visual.")

    s_get = s_subs.add_parser("get", help="Obtém o código HTML/CSS e assets de uma tela.")
    s_get.add_argument("--screen-id", "-s", required=True, help="ID da tela.")

    s_vars = s_subs.add_parser("variants", help="Gera variantes visuais exploratórias de uma tela.")
    s_vars.add_argument("--screen-id", "-s", required=True, help="ID da tela base.")
    s_vars.add_argument("--prompt", "-p", required=True, help="Instruções de variação.")
    s_vars.add_argument("--count", "-c", type=int, default=3, help="Número de variantes (padrão: 3).")

    s_sync = s_subs.add_parser("sync", help="Sincroniza design tokens do design.md com o Design System do Stitch.")
    s_sync.add_argument("--file", "-f", help="Caminho do arquivo design.md.")
    p_stitch.set_defaults(func=cmd_stitch)

    # 9. amb render
    p_render = subparsers.add_parser("render", help="Comandos de integração com o Render Cloud.")
    r_subs = p_render.add_subparsers(dest="render_cmd", help="Subcomandos do Render")
    r_subs.add_parser("status", help="Status do deploy mais recente.")
    r_subs.add_parser("logs", help="Últimos logs de build/execução.")
    r_subs.add_parser("deploy", help="Dispara um novo deploy.")
    r_subs.add_parser("services", help="Lista todos os serviços configurados na conta Render.")
    p_render.set_defaults(func=cmd_render)

    # 10. amb validate
    p_val = subparsers.add_parser("validate", aliases=["lint", "audit"], help="Audita um arquivo contra as regras arquiteturais do repositório.")
    p_val.add_argument("file", help="Caminho do arquivo de código a ser auditado.")
    p_val.set_defaults(func=cmd_validate)

    # 11. amb pipeline
    p_pipe = subparsers.add_parser("pipeline", help="Executa o pipeline orquestrado Design-to-Deploy ponta a ponta.")
    p_pipe.add_argument("template", nargs="?", default=None, help="Caminho do arquivo markdown de especificação da tarefa.")
    p_pipe.add_argument("--auto-approve", "-y", action="store_true", help="Pula confirmações manuais no Gatekeeper 1 de Design.")
    p_pipe.add_argument("--skip-stitch", action="store_true", help="Pula a etapa de layout visual do Stitch e vai direto à engenharia no Jules.")
    p_pipe.add_argument("--no-qa", action="store_true", help="Não executa a verificação local pós-sessão de typecheck/build.")
    p_pipe.add_argument("--resume-session", "-r", help="Retoma o monitoramento de uma sessão existente do Jules.")
    p_pipe.add_argument("--device-type", choices=["DESKTOP", "MOBILE", "TABLET"], default="DESKTOP", help="Tipo de dispositivo para renderização no Stitch.")
    p_pipe.add_argument("--screen-id", "-s", help="ID de tela existente no Stitch para reaproveitar como base.")
    p_pipe.add_argument("--edit-screen", help="ID de tela existente para refinar com novo prompt.")
    p_pipe.add_argument("--sync-ds", action="store_true", help="Sincroniza os design tokens locais com o Stitch antes de iniciar.")
    p_pipe.add_argument("--branch", "-b", default="develop", help="Branch de início para o Jules (Padrão: develop).")
    p_pipe.set_defaults(func=cmd_pipeline)


    # 12. amb schema (alias: amb db)
    p_schema = subparsers.add_parser("schema", aliases=["db"], help="Inspeciona tabelas e colunas de schemas do banco de dados (Read-Only).")
    p_schema.add_argument("target", nargs="?", default=None, help="Nome da tabela ou módulo a filtrar (ex: kanban, agenda, projects).")
    p_schema.set_defaults(func=cmd_schema)

    # 13. amb context (alias: amb ctx)
    p_ctx = subparsers.add_parser("context", aliases=["ctx", "ai-context"], help="Gera o roteiro de leitura de arquivos por camadas para a IA.")
    p_ctx.add_argument("module", nargs="?", default="agenda", help="Nome do módulo ou pasta para rastrear (ex: agenda, kanban, projects).")
    p_ctx.add_argument("--json", action="store_true", help="Retorna o resultado em JSON estruturado.")
    p_ctx.set_defaults(func=cmd_context)

    return parser
