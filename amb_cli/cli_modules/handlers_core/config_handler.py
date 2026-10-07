import os
from typing import Any
from amb_cli.core import Colors
from amb_cli.core.config_manager import ConfigManager
from amb_cli.core.env import is_gemini_confirmation_required, set_gemini_confirmation


def handle_cmd_config(args: Any) -> None:
    """Gerencia preferências e controles do AMB_V2 (ex: reload cache, gemini confirm)."""
    # 1. Tratar subcomando/ação "reload"
    action = getattr(args, "config_action", None)
    if action == "reload":
        config = ConfigManager.get_instance()
        config.reload()

        # Opcional: mostrar quantas chaves foram recarregadas para o resumo
        env_keys = len(config._cached_env)
        proj_keys = len(config._cached_project)

        print(f"\n{Colors.GREEN}✅ Configurações recarregadas com sucesso.{Colors.RESET}")
        print(f"📦 Resumo do Cache em Memória:")
        print(f"   - Variáveis de ambiente (.env): {env_keys} carregadas.")
        print(f"   - Metadados do projeto (amb_project.json): {proj_keys} chaves.")
        return

    # 2. Tratar flag "--gemini-confirm"
    if getattr(args, "gemini_confirm", None) is not None:
        enable = args.gemini_confirm.lower() in ["on", "true", "1", "yes", "sim", "ativar"]
        set_gemini_confirmation(enable)
        status_msg = f"{Colors.GREEN}ATIVADA (Exige confirmação interativa antes de cada requisição ao Gemini){Colors.RESET}" if enable else f"{Colors.YELLOW}DESATIVADA (Chamadas ao Gemini automáticas){Colors.RESET}"
        print(f"\n🛡️ Autorização prévia do Gemini: {status_msg}\n")
    else:
        status = is_gemini_confirmation_required()
        status_msg = f"{Colors.GREEN}ATIVADA (Exige confirmação manual){Colors.RESET}" if status else f"{Colors.DIM}DESATIVADA (Chamadas automáticas){Colors.RESET}"
        print(f"\n🛡️ Status da Autorização do Gemini: {status_msg}")
        print(f"👉 Para alterar: amb config --gemini-confirm on (ou off)")
        print(f"👉 Para recarregar configs: amb config reload\n")
