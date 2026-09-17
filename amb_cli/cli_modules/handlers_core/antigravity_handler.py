import json
from typing import Any
from config.bootstrap import ensure_amb_env

ensure_amb_env()

def handle_cmd_antigravity(args: Any) -> None:
    """Implementação isolada do comando antigravity."""
    sub = getattr(args, "agy_cmd", None)
    from integrations.antigravity.antigravity_client import AntigravityClient
    from config import Colors, log, get_rules_manager

    if sub in ["status", "check", None]:
        client = AntigravityClient()
        status_data = client.get_status()
        if getattr(args, "json", False):
            print(json.dumps(status_data, indent=2, ensure_ascii=False))
            return
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== 🧠 DIAGNÓSTICO GOOGLE ANTIGRAVITY ==={Colors.RESET}\n")
        status_color = Colors.GREEN if status_data["status"] == "OK" else Colors.YELLOW
        print(f"  • Status Geral: {status_color}{status_data['status']}{Colors.RESET}")
        print(f"  • Modelo Ativo: {Colors.BOLD}{status_data['model']}{Colors.RESET}")
        api_st = f"{Colors.GREEN}Configurada{Colors.RESET}" if status_data["gemini_api_key_configured"] else f"{Colors.RED}Não configurada{Colors.RESET}"
        print(f"  • GEMINI_API_KEY: {api_st}")
        agy_st = f"{Colors.GREEN}Instalada ({status_data['agy_cli_path']}){Colors.RESET}" if status_data["agy_cli_installed"] else f"{Colors.YELLOW}Não encontrada (usando REST API){Colors.RESET}"
        print(f"  • CLI agy: {agy_st}")
        rules_dir_str = status_data["rules_directory"] or "Nenhum diretório de regras encontrado"
        print(f"  • Diretório de Regras: {Colors.DIM}{rules_dir_str}{Colors.RESET} ({status_data['rules_count']} regras)")
        if status_data["rules"]:
            print(f"    Regras ativas: {', '.join(status_data['rules'])}")
        print()

    elif sub in ["prompt", "synthesize", "synth"]:
        from integrations.antigravity.tools.synthesize_prompt import run_synthesize_prompt
        idea = getattr(args, "idea", "")
        role = getattr(args, "role", "general") or "general"
        output_file = getattr(args, "output", None)
        log("ANTIGRAVITY", f"Sintetizando prompt executivo ({role})...", Colors.CYAN)
        res = run_synthesize_prompt(raw_idea=idea, role=role, output_file=output_file)
        if not output_file:
            print("\n" + "=" * 75)
            print(f"{Colors.BOLD}🧠 PROMPT ESTRUTURADO GERADO COM IA:{Colors.RESET}")
            print("=" * 75)
            print(res)
            print("=" * 75 + "\n")

    elif sub in ["validate", "audit", "lint"]:
        from integrations.antigravity.tools.validate_architecture import run_validate_architecture
        target_file = getattr(args, "file", "")
        log("ANTIGRAVITY", f"Auditando conformidade arquitetural de {target_file}...", Colors.CYAN)
        res = run_validate_architecture(file_path=target_file)
        if getattr(args, "json", False):
            print(json.dumps({"file": target_file, "report": res}, indent=2, ensure_ascii=False))
            return
        print("\n" + "=" * 75)
        print(f"{Colors.BOLD}RELATÓRIO DE AUDITORIA ARQUITETURAL:{Colors.RESET}")
        print("=" * 75)
        print(res)
        print("=" * 75 + "\n")

    elif sub == "rules":
        mgr = get_rules_manager()
        rules_dir = mgr.resolve_rules_dir()
        rules_list = mgr.list_rules(rules_dir=rules_dir)
        as_json = getattr(args, "json", False)
        show_content = getattr(args, "content", False)

        if as_json:
            out = {
                "rules_directory": rules_dir,
                "rules": rules_list
            }
            if show_content:
                out["consolidated_content"] = mgr.load_rules(rules_dir=rules_dir)
            print(json.dumps(out, indent=2, ensure_ascii=False))
            return

        print(f"\n{Colors.BOLD}{Colors.CYAN}=== 📋 REGRAS ARQUITETURAIS DO REPOSITÓRIO ==={Colors.RESET}\n")
        print(f"Diretório: {Colors.DIM}{rules_dir or 'Nenhum'}{Colors.RESET} ({len(rules_list)} arquivo(s))\n")
        for r in rules_list:
            print(f"  • {Colors.BOLD}{r['name']:<25}{Colors.RESET} ({r['size_bytes']} bytes)")
            if r["summary"]:
                print(f"    {Colors.DIM}{r['summary']}{Colors.RESET}")
        print()
        if show_content:
            content = mgr.load_rules(rules_dir=rules_dir)
            print("=" * 75)
            print(f"{Colors.BOLD}CONTEÚDO CONSOLIDADO DAS REGRAS:{Colors.RESET}")
            print("=" * 75)
            print(content)
            print("=" * 75 + "\n")

    elif sub in ["run", "eval"]:
        prompt_text = getattr(args, "prompt", "")
        system_text = getattr(args, "system", None)
        model_override = getattr(args, "model", None)
        temp = getattr(args, "temperature", 0.2)
        client = AntigravityClient(model=model_override)
        log("ANTIGRAVITY", f"Executando inferência com {client.model}...", Colors.CYAN)
        res = client.generate_text(
            prompt=prompt_text,
            system_instruction=system_text,
            temperature=temp
        )
        out_f = getattr(args, "output", None)
        if out_f:
            with open(out_f, "w", encoding="utf-8") as f:
                f.write(res)
            log("ANTIGRAVITY", f"Resposta salva em {out_f}", Colors.GREEN)
        else:
            print(res)

    else:
        print("Subcomando do Antigravity inválido. Use 'amb agy --help'.")
