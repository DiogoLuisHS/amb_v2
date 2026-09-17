import argparse
from cli_modules.cli_handlers import (
    cmd_setup, cmd_prompt, cmd_check, cmd_monitor, cmd_advisor, cmd_gui,
    cmd_config, cmd_agent, cmd_jules, cmd_stitch, cmd_validate,
    cmd_pipeline, cmd_schema, cmd_context, cmd_antigravity, cmd_git
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
    p_setup.add_argument("--path", help="Diretório alvo específico para configurar (padrão: diretório atual).")
    p_setup.add_argument("--force", action="store_true", help="Sobrescreve arquivos de template existentes.")
    p_setup.add_argument("--dry-run", action="store_true", help="Simula a execução do setup sem escrever nada no disco.")
    p_setup.add_argument("--prompt", "-p", action="store_true", help="Exibe o Prompt Mestre de Auto-Configuração para colar em IAs.")
    p_setup.set_defaults(func=cmd_setup)

    # 1.1 amb prompt
    p_prompt = subparsers.add_parser("prompt", help="Exibe ou sintetiza com IA o Prompt de Desenvolvimento.")
    p_prompt.add_argument("--synthesize", "-s", help="Ideia informal a ser sintetizada em prompt estruturado com IA.")
    p_prompt.add_argument("--role", "-r", default="general", help="Especialidade para sintetização do prompt.")
    p_prompt.set_defaults(func=cmd_prompt)

    # 2. amb check
    p_check = subparsers.add_parser("check", aliases=["status"], help="Valida chaves e configurações do projeto ativo.")
    p_check.add_argument("--json", action="store_true", help="Exibe o diagnóstico em formato JSON estruturado.")
    p_check.set_defaults(func=cmd_check)

    # 2.1 amb config
    p_cfg = subparsers.add_parser("config", aliases=["settings", "pref"], help="Configura preferências de IA, quotas e autorizações do AMB_V2.")
    p_cfg.add_argument("--gemini-confirm", choices=["on", "off", "true", "false"], help="Ativa (on) ou desativa (off) a exigência de autorização manual a cada chamada ao Gemini.")
    p_cfg.set_defaults(func=cmd_config)


    # 3. amb monitor
    p_mon = subparsers.add_parser("monitor", aliases=["watch", "sentinel"], help="Sentinela em tempo real (Jules) com suporte a auto-resposta Gemini.")
    p_mon.add_argument("--interactive", "-i", action="store_true", help="Abre o menu interativo cognitivo (Advisor) para inspecionar e responder pendências.")
    p_mon.add_argument("--auto-approve", "-y", action="store_true", help="Aprova e responde chats automaticamente via Gemini.")
    p_mon.add_argument("--check-once", "-1", action="store_true", help="Executa apenas uma rodada de checagem e encerra.")
    p_mon.add_argument("--interval", type=int, default=15, help="Intervalo de polling em segundos (padrão: 15s).")
    p_mon.set_defaults(func=cmd_monitor)

    # 4. amb advisor
    p_adv = subparsers.add_parser("advisor", aliases=["ask"], help="Menu cognitivo para tirar dúvidas pendentes do Jules com IA.")
    p_adv.add_argument("session_id", nargs="?", help="ID ou URL da sessão do Jules (opcional).")
    p_adv.add_argument("--session-id", "-s", dest="session_id_flag", help="ID ou URL da sessão do Jules.")
    p_adv.add_argument("--message", "-m", help="Mensagem direta manual a ser enviada ao chat.")
    p_adv.add_argument("--auto-approve", "-y", action="store_true", help="Responde ou aprova automaticamente com IA sem confirmação.")
    p_adv.set_defaults(func=cmd_advisor)

    # 5. amb gui
    p_gui = subparsers.add_parser("gui", aliases=["ui", "wizard"], help="Abre o Assistente Gráfico Interativo (UI Wizard) para montagem de comandos e gestão de ambiente (.env).")
    p_gui.set_defaults(func=cmd_gui)

    # 6. amb agent
    p_agent = subparsers.add_parser("agent", aliases=["persona"], help="Executor de personas autônomas de manutenção.")
    p_agent.add_argument("--role", "-r", help="Nome da persona (ex: engineer, etc.).")
    p_agent.add_argument("--all", "-a", action="store_true", help="Executa todas as personas em lote.")
    p_agent.add_argument("--prompt", "-p", help="Caminho de um arquivo markdown (.md) com prompt estruturado.")
    p_agent.add_argument("--task", "-t", help="Instruções ou escopo adicional.")
    p_agent.add_argument("--list", "-l", action="store_true", help="Lista todas as personas disponíveis.")
    p_agent.add_argument("--agy", "--local", action="store_true", default=False, help="Executa o agente localmente via agy CLI (por padrão despacha para o Google Jules na nuvem).")
    p_agent.add_argument("--dispatch-jules", "-j", action="store_true", help="(Legado) Força o despacho para o Google Jules (comportamento padrão).")
    p_agent.add_argument("--loop", "-c", "--continuous", action="store_true", help="Executa o ciclo contínuo e autônomo de personas.")
    p_agent.add_argument("--max-cycles", type=int, help="Limite de ciclos no modo loop (se omitido, roda continuamente).")
    p_agent.add_argument("--branch", "-b", help="Branch de início para o Jules (se omitido, auto-detecta a branch ativa do Git).")
    p_agent.add_argument("--personas-dir", help="Pasta customizada de personas.")
    p_agent.set_defaults(func=cmd_agent)


    # 7. amb jules
    p_jules = subparsers.add_parser("jules", help="Comandos de integração com o Google Jules.")
    j_subs = p_jules.add_subparsers(dest="jules_cmd", help="Subcomandos do Jules")

    j_status = j_subs.add_parser("status", aliases=["check"], help="Diagnóstico de conectividade, credenciais e sessões ativas do Jules.")
    j_status.add_argument("--repo", "-r", help="Filtra o diagnóstico por repositório específico.")
    j_status.add_argument("--json", action="store_true", help="Exibe o diagnóstico em formato JSON puro.")

    j_sources = j_subs.add_parser("sources", aliases=["source"], help="Lista fontes e repositórios conectados à conta Google Jules.")
    j_sources.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")

    j_list = j_subs.add_parser("list", help="Lista sessões recentes do repositório ou de toda a conta.")
    j_list.add_argument("--limit", "-n", type=int, default=10, help="Limite de sessões exibidas (padrão: 10).")
    j_list.add_argument("--all", "-a", action="store_true", help="Lista sessões de todos os repositórios (desativa filtro por repo atual).")
    j_list.add_argument("--repo", "-r", help="Filtra por repositório específico (ex: org/repo).")
    j_list.add_argument("--state", "-s", help="Filtra por estado (ex: AWAITING_USER_FEEDBACK, IN_PROGRESS, COMPLETED, FAILED).")
    j_list.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")

    j_get = j_subs.add_parser("get", help="Exibe detalhes, PR ou faz streaming ao vivo da sessão.")
    j_get.add_argument("session_id", nargs="?", help="ID ou URL da sessão do Jules.")
    j_get.add_argument("--session-id", "-s", dest="session_id_flag", help="ID ou URL da sessão (flag alternativa).")
    j_get.add_argument("--watch", "-w", action="store_true", help="Acompanha em tempo real as atividades e saídas da sessão.")
    j_get.add_argument("--json", action="store_true", help="Saída em formato JSON puro.")

    j_create = j_subs.add_parser("create", help="Cria uma nova sessão no Jules Cloud VM.")
    j_create.add_argument("--prompt", "-p", required=True, help="Prompt ou caminho de arquivo com instruções da tarefa.")
    j_create.add_argument("--title", "-t", help="Título descritivo da sessão.")
    j_create.add_argument("--branch", "-b", help="Branch base inicial no repositório (padrão: auto-detecta a branch ativa do Git).")
    j_create.add_argument("--source", help="Fonte conectada no Jules (padrão: auto-detecta sources/github/owner/repo).")
    j_create.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")

    j_reply = j_subs.add_parser("reply", aliases=["advisor", "ask"], help="Responde uma dúvida com IA (ou envia mensagem direta se --message).")
    j_reply.add_argument("session_id", nargs="?", help="ID ou URL da sessão do Jules (opcional).")
    j_reply.add_argument("--session-id", "-s", dest="session_id_flag", required=False, help="ID ou URL da sessão (opcional; se omitido, lista todas as sessões pendentes).")
    j_reply.add_argument("--message", "-m", help="Mensagem direta manual a ser enviada ao chat.")
    j_reply.add_argument("--auto-approve", "-y", action="store_true", help="Envia resposta gerada pelo Gemini sem pedir confirmação.")
    j_reply.add_argument("--force", "-f", action="store_true", help="Força envio ignorando guardrail de mensagens consecutivas do usuário.")

    j_app = j_subs.add_parser("approve", help="Aprova o plano de execução de uma sessão.")
    j_app.add_argument("session_id", nargs="?", help="ID ou URL da sessão do Jules.")
    j_app.add_argument("--session-id", "-s", dest="session_id_flag", help="ID ou URL da sessão (flag alternativa).")
    j_app.add_argument("--force", "-f", action="store_true", help="Força aprovação sem checar se o plano está em estado pendente.")
    j_app.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")

    j_merge = j_subs.add_parser("merge", help="Detecta o PR da sessão, aprova, faz merge no GitHub e valida localmente.")
    j_merge.add_argument("session_id", nargs="?", help="ID ou URL da sessão do Jules para detectar o PR.")
    j_merge.add_argument("--session-id", "-s", dest="session_id_flag", help="ID da sessão para detectar o PR (flag alternativa).")
    j_merge.add_argument("--auto-latest", "-a", action="store_true", help="Detecta automaticamente o PR aberto mais recente.")
    j_merge.add_argument("--branch", "-b", default="main", help="Branch de destino local após merge (padrão: main).")

    j_clean = j_subs.add_parser("clean", aliases=["cleanup"], help="Audita e remove na nuvem sessões do Jules já integradas.")
    j_clean.add_argument("--force", "-f", action="store_true", help="Remove sem pedir confirmação.")
    j_clean.add_argument("--failed", action="store_true", help="Remove todas as sessões que estão em estado de falha (FAILED).")
    j_clean.add_argument("--merged", action="store_true", help="Remove sessões cujos PRs já foram integrados ao Git.")
    j_clean.add_argument("--id", help="Remove uma sessão específica por ID.")
    p_jules.set_defaults(func=cmd_jules)

    # 8. amb stitch
    p_stitch = subparsers.add_parser("stitch", help="Comandos de integração com o Google Stitch SDK.")
    s_subs = p_stitch.add_subparsers(dest="stitch_cmd", help="Subcomandos do Stitch")

    s_list = s_subs.add_parser("list", help="Lista todas as telas geradas no projeto Stitch.")
    s_list.add_argument("--project-id", help="ID do projeto Stitch (padrão: lê do .env).")
    s_list.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")

    s_gen = s_subs.add_parser("generate", help="Gera uma nova tela via Stitch.")
    s_gen.add_argument("--prompt", "-p", required=True, help="Descrição visual da tela.")
    s_gen.add_argument("--title", "-t", help="Título da tela.")
    s_gen.add_argument("--device", "-d", choices=["DESKTOP", "MOBILE", "TABLET", "AGNOSTIC"], default=None, help="Tipo de dispositivo alvo (DESKTOP, MOBILE, TABLET, AGNOSTIC; padrão: lê do projeto ou .env).")
    s_gen.add_argument("--output", "-o", help="Caminho do arquivo para salvar o HTML da tela.")
    s_gen.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")

    s_ref = s_subs.add_parser("refine", help="Refina uma tela existente no Stitch com novas instruções.")
    s_ref.add_argument("--screen-id", "-s", required=True, help="ID da tela.")
    s_ref.add_argument("--prompt", "-p", required=True, help="Instruções de edição e refinamento visual.")
    s_ref.add_argument("--device", "-d", choices=["DESKTOP", "MOBILE", "TABLET", "AGNOSTIC"], default=None, help="Tipo de dispositivo alvo.")
    s_ref.add_argument("--output", "-o", help="Caminho do arquivo para salvar o novo HTML refinado.")
    s_ref.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")

    s_get = s_subs.add_parser("get", help="Obtém o código HTML/CSS e assets de uma tela.")
    s_get.add_argument("--screen-id", "-s", required=True, help="ID da tela.")
    s_get.add_argument("--output", "-o", help="Caminho do arquivo para salvar o código HTML da tela.")
    s_get.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")

    s_vars = s_subs.add_parser("variants", help="Gera variantes visuais exploratórias de uma tela.")
    s_vars.add_argument("--screen-id", "-s", required=True, help="ID da tela base.")
    s_vars.add_argument("--prompt", "-p", required=True, help="Instruções de variação.")
    s_vars.add_argument("--count", "-c", type=int, default=3, help="Número de variantes (padrão: 3).")
    s_vars.add_argument("--device", "-d", choices=["DESKTOP", "MOBILE", "TABLET", "AGNOSTIC"], default=None, help="Tipo de dispositivo alvo.")
    s_vars.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")

    s_down = s_subs.add_parser("download", help="Baixa todas as telas e assets do projeto Stitch para um diretório local.")
    s_down.add_argument("--output", "-o", default="./stitch_assets", help="Diretório local de destino dos assets baixados.")
    s_down.add_argument("--project-id", help="ID do projeto Stitch (padrão: lê do .env).")
    s_down.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")

    s_proj = s_subs.add_parser("project", help="Consulta detalhes do projeto Stitch ativo.")
    s_proj.add_argument("--project-id", help="ID do projeto Stitch (padrão: lê do .env).")
    s_proj.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")

    s_sync = s_subs.add_parser("sync", help="Sincroniza design tokens do design.md com o Design System do Stitch.")
    s_sync.add_argument("--file", "-f", help="Caminho do arquivo design.md.")
    s_sync.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")

    s_call = s_subs.add_parser("call", help="Invoca uma ferramenta arbitrária do Stitch SDK via JSON-RPC.")
    s_call.add_argument("tool", help="Nome da ferramenta (ex: get_screen, list_screens, download_assets).")
    s_call.add_argument("payload", nargs="?", default="{}", help="Payload JSON da ferramenta.")
    s_call.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")
    p_stitch.set_defaults(func=cmd_stitch)

    # 9. amb antigravity (alias: amb agy)
    p_agy = subparsers.add_parser("antigravity", aliases=["agy"], help="Comandos de inferência cognitiva e SDK Google Antigravity.")
    agy_subs = p_agy.add_subparsers(dest="agy_cmd", help="Subcomandos do Antigravity")

    a_status = agy_subs.add_parser("status", aliases=["check"], help="Verifica status do runtime agy, chaves e regras ativas.")
    a_status.add_argument("--json", action="store_true", help="Exibe o status em formato JSON estruturado.")

    a_prompt = agy_subs.add_parser("prompt", aliases=["synthesize", "synth"], help="Sintetiza uma ideia informal em prompt executivo formal com IA.")
    a_prompt.add_argument("--idea", "-i", required=True, help="Ideia informal ou requisito a sintetizar.")
    a_prompt.add_argument("--role", "-r", default="general", help="Especialidade ou papel da persona (padrão: general).")
    a_prompt.add_argument("--output", "-o", help="Caminho do arquivo para salvar o prompt sintetizado.")

    a_val = agy_subs.add_parser("validate", aliases=["audit", "lint"], help="Audita conformidade arquitetural de um arquivo contra as regras do repositório.")
    a_val.add_argument("file", help="Caminho do arquivo a ser auditado.")
    a_val.add_argument("--json", action="store_true", help="Exibe o relatório em JSON estruturado.")

    a_rules = agy_subs.add_parser("rules", help="Lista e inspeciona as regras arquiteturais descobertas no projeto.")
    a_rules.add_argument("--json", action="store_true", help="Exibe a lista de regras em JSON.")
    a_rules.add_argument("--content", "-c", action="store_true", help="Exibe o conteúdo integral consolidado das regras.")

    a_run = agy_subs.add_parser("run", aliases=["eval"], help="Executa inferência direta com prompt arbitrário via modelo cognitivo.")
    a_run.add_argument("prompt", help="Prompt para inferência cognitiva.")
    a_run.add_argument("--system", "-s", help="Instrução de sistema opcional.")
    a_run.add_argument("--model", "-m", help="Modelo específico do Gemini (ex: gemini-3.8-flash).")
    a_run.add_argument("--temperature", "-t", type=float, default=0.2, help="Temperatura de amostragem (padrão: 0.2).")
    a_run.add_argument("--output", "-o", help="Salva a saída em arquivo.")
    p_agy.set_defaults(func=cmd_antigravity)

    # 10. amb validate
    p_val = subparsers.add_parser("validate", aliases=["lint", "audit"], help="Audita um arquivo contra as regras arquiteturais do repositório.")
    p_val.add_argument("file", help="Caminho do arquivo de código a ser auditado.")
    p_val.set_defaults(func=cmd_validate)

    # 11. amb pipeline
    p_pipe = subparsers.add_parser("pipeline", aliases=["run", "deploy"], help="Roda o orquestrador Design-to-Deploy (Stitch -> Jules -> GitHub) com prompts separados para Design e Engenharia.")
    p_pipe.add_argument("--stitch-prompt", "-s", help="Caminho do arquivo markdown contendo a especificação visual para o Stitch.")
    p_pipe.add_argument("--jules-prompt", "-j", help="Caminho do arquivo markdown contendo as instruções técnicas para o Jules.")
    p_pipe.add_argument("--prompt-file", "-f", help="Arquivo único unificado (.md) com divisões claras entre [STITCH_DESIGN] e [JULES_DEV].")
    p_pipe.add_argument("--resume-session", "-r", help="ID da sessão Jules para retomar o monitoramento sem criar nova.")
    p_pipe.add_argument("--skip-stitch", action="store_true", help="Pula a geração de UI no Stitch, indo direto ao Jules.")
    p_pipe.add_argument("--no-qa", action="store_true", help="Desabilita o teste QA local automático no final.")
    p_pipe.add_argument("--auto-approve", "-y", action="store_true", help="Aprova planos no Jules automaticamente.")
    p_pipe.add_argument("--repo", help="Repositório GitHub no formato 'dono/repo' (padrão: auto-detectado via git).")
    p_pipe.add_argument("--device", "-d", choices=["DESKTOP", "MOBILE", "TABLET", "AGNOSTIC"], default=None, help="Tipo de dispositivo para geração do Stitch.")
    p_pipe.add_argument("--edit-screen-id", help="Refina uma tela existente no Stitch em vez de criar uma nova.")
    p_pipe.add_argument("--screen-id", help="Utiliza uma tela já existente no Stitch como ponto de partida (não recria).")
    p_pipe.add_argument("--sync-ds", action="store_true", help="Sincroniza os design tokens locais antes de gerar a tela.")
    p_pipe.add_argument("--branch", "-b", help="Branch alvo para PR e checkout (default: detecta a atual).")
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

    # 14. amb git
    p_git = subparsers.add_parser("git", help="Comandos de controle de versão e ciclo de vida de Pull Requests via Git & GitHub CLI.")
    git_subs = p_git.add_subparsers(dest="git_cmd", help="Subcomandos do Git")

    g_status = git_subs.add_parser("status", help="Exibe status detalhado do repositório Git, branches, upstream e GitHub CLI.")
    g_status.add_argument("--json", action="store_true", help="Exibe o status em formato JSON estruturado.")

    g_sync = git_subs.add_parser("sync", help="Sincroniza a branch ativa com o repositório remoto (fetch + pull com auto-stash).")
    g_sync.add_argument("--remote", "-r", default="origin", help="Nome do remote (padrão: origin).")
    g_sync.add_argument("--branch", "-b", help="Nome da branch (padrão: branch ativa).")
    g_sync.add_argument("--no-stash", action="store_false", dest="auto_stash", help="Desabilita stash automático se a working tree estiver modificada.")

    g_diff = git_subs.add_parser("diff", help="Exibe o diff unificado de arquivos alterados ou contra a branch base.")
    g_diff.add_argument("file", nargs="?", default=None, help="Caminho do arquivo específico (opcional).")
    g_diff.add_argument("--base", "-b", help="Branch base para comparação.")
    g_diff.add_argument("--cached", action="store_true", help="Exibe diff das alterações preparadas (staged).")

    g_pr = git_subs.add_parser("pr", help="Gerenciador de Pull Requests no GitHub via GitHub CLI.")
    pr_subs = g_pr.add_subparsers(dest="pr_cmd", help="Ações de Pull Request")

    pr_list = pr_subs.add_parser("list", help="Lista Pull Requests abertos no repositório.")
    pr_list.add_argument("--repo", help="Repositório alvo (dono/repo).")
    pr_list.add_argument("--no-drafts", action="store_true", help="Oculta PRs em modo draft.")
    pr_list.add_argument("--json", action="store_true", help="Exibe a lista em JSON puro.")

    pr_get = pr_subs.add_parser("get", help="Exibe detalhes completos de um Pull Request.")
    pr_get.add_argument("number", type=int, help="Número do Pull Request.")
    pr_get.add_argument("--repo", help="Repositório alvo (dono/repo).")
    pr_get.add_argument("--json", action="store_true", help="Exibe os detalhes em JSON puro.")

    pr_create = pr_subs.add_parser("create", help="Cria um novo Pull Request no GitHub.")
    pr_create.add_argument("--title", "-t", required=True, help="Título do PR.")
    pr_create.add_argument("--body", "-b", default="", help="Descrição detalhada do PR.")
    pr_create.add_argument("--base", help="Branch base de destino.")
    pr_create.add_argument("--head", help="Branch de origem das alterações.")
    pr_create.add_argument("--draft", action="store_true", help="Cria o PR como rascunho (Draft).")
    pr_create.add_argument("--repo", help="Repositório alvo.")
    pr_create.add_argument("--json", action="store_true", help="Exibe o retorno em JSON.")

    pr_ready = pr_subs.add_parser("ready", help="Marca um PR em draft como pronto para revisão.")
    pr_ready.add_argument("number", type=int, help="Número do Pull Request.")
    pr_ready.add_argument("--repo", help="Repositório alvo.")

    pr_app = pr_subs.add_parser("approve", help="Aprova formalmente o Pull Request.")
    pr_app.add_argument("number", type=int, help="Número do Pull Request.")
    pr_app.add_argument("--body", default="✅ Aprovado pelo AMB_V2.", help="Comentário de aprovação.")
    pr_app.add_argument("--repo", help="Repositório alvo.")

    pr_merge = pr_subs.add_parser("merge", help="Realiza o merge do Pull Request.")
    pr_merge.add_argument("number", type=int, help="Número do Pull Request.")
    pr_merge.add_argument("--no-squash", action="store_false", dest="squash", help="Não realizar squash merge.")
    pr_merge.add_argument("--keep-branch", action="store_false", dest="delete_branch", help="Não deletar a branch remota após merge.")
    pr_merge.add_argument("--repo", help="Repositório alvo.")

    pr_close = pr_subs.add_parser("close", help="Fecha um Pull Request no GitHub.")
    pr_close.add_argument("number", type=int, help="Número do Pull Request.")
    pr_close.add_argument("--comment", help="Comentário opcional ao fechar.")
    pr_close.add_argument("--delete-branch", action="store_true", help="Deletar a branch associada.")
    pr_close.add_argument("--repo", help="Repositório alvo.")

    p_git.set_defaults(func=cmd_git)

    return parser
