import json
import os
from typing import Any, Optional
from core.bootstrap import ensure_amb_env

ensure_amb_env()

def handle_cmd_antigravity(args: Any) -> None:
    """Implementação isolada do comando antigravity."""
    sub = getattr(args, "agy_cmd", None)
    from core import Colors, log
    from integrations.antigravity.antigravity_client import AntigravityClient
    from workspace import get_rules_manager

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
        import os
        from core.logger import log_error
        from integrations.antigravity.tools.synthesize_prompt import run_synthesize_prompt

        raw_idea = getattr(args, "idea", None) or getattr(args, "idea_flag", None) or getattr(args, "synthesize_flag", None)

        if not raw_idea:
            log_error("ANTIGRAVITY", "Nenhuma ideia ou arquivo fornecido. Use: amb agy prompt 'Sua ideia' ou passe um arquivo.")
            return

        if os.path.isfile(raw_idea):
            with open(raw_idea, "r", encoding="utf-8", errors="replace") as f:
                raw_idea = f.read().strip()

        role = getattr(args, "role", "general") or "general"
        output_file = getattr(args, "output", None)
        image_path = getattr(args, "image", None)
        queue_flag = getattr(args, "queue", False)

        log("ANTIGRAVITY", f"Sintetizando prompt executivo ({role})" + (f" com mockup '{image_path}'..." if image_path else "..."), Colors.CYAN)
        res = run_synthesize_prompt(raw_idea=raw_idea, role=role, output_file=output_file, image_path=image_path, queue=queue_flag)
        if not output_file and not queue_flag:
            print("\n" + "=" * 75)
            print(f"{Colors.BOLD}🧠 PROMPT ESTRUTURADO GERADO COM IA:{Colors.RESET}")
            print("=" * 75)
            print(res)
            print("=" * 75 + "\n")

    elif sub in ["validate", "audit", "lint"]:
        from integrations.antigravity.tools.validate_architecture import run_validate_architecture
        import sys

        is_staged = getattr(args, "staged", False)

        files_to_check = []
        if is_staged:
            mgr = get_rules_manager()
            staged_files = mgr.get_staged_files()
            if not staged_files:
                print(f"\n{Colors.CYAN}Nenhum arquivo no stage (git add) para auditar.{Colors.RESET}")
                return
            files_to_check = staged_files
        else:
            target_file = getattr(args, "file", None)
            if not target_file:
                log("VALIDATE", "Nenhum arquivo especificado. Executando validação de integridade do projeto (QA)...", Colors.CYAN)
                from pipeline.quality_gatekeeper import QualityGatekeeper
                qa_ok = QualityGatekeeper.run_qa()
                if getattr(args, "json", False):
                    print(json.dumps({"status": "SUCCESS" if qa_ok else "FAILED", "qa_passed": qa_ok}, indent=2))
                if not qa_ok:
                    sys.exit(1)
                return
            files_to_check = [target_file]

        reports = []
        has_violations = False

        fix_flag = getattr(args, "fix", False)

        for file in files_to_check:
            log("ANTIGRAVITY", f"Auditando conformidade arquitetural de {file}...", Colors.CYAN)
            res = run_validate_architecture(file_path=file)

            # Simple heuristic to detect violation
            res_lower = res.lower()
            file_has_violations = False
            if "violação" in res_lower or "violacao" in res_lower or "não conform" in res_lower or "falha" in res_lower or "erro" in res_lower or "issue" in res_lower:
                has_violations = True
                file_has_violations = True

            reports.append({"file": file, "report": res})

            if not getattr(args, "json", False):
                print("\n" + "=" * 75)
                print(f"{Colors.BOLD}RELATÓRIO DE AUDITORIA ARQUITETURAL: {file}{Colors.RESET}")
                print("=" * 75)
                print(res)
                print("=" * 75 + "\n")

            if fix_flag and file_has_violations:
                from integrations.antigravity.tools.validate_architecture import generate_architecture_fix
                import difflib

                log("ANTIGRAVITY", f"Gerando proposta de correção para {file}...", Colors.CYAN)
                fixed_content = generate_architecture_fix(file_path=file, report=res)

                if fixed_content:
                    with open(file, "r", encoding="utf-8", errors="replace") as f:
                        original_content = f.read()

                    if original_content != fixed_content:
                        diff = difflib.unified_diff(
                            original_content.splitlines(keepends=True),
                            fixed_content.splitlines(keepends=True),
                            fromfile=f"a/{file}",
                            tofile=f"b/{file}",
                        )
                        diff_str = "".join(diff)

                        print(f"\n{Colors.BOLD}{Colors.YELLOW}Proposta de Correção para {file}:{Colors.RESET}")
                        for line in diff_str.splitlines():
                            if line.startswith("+") and not line.startswith("+++"):
                                print(f"{Colors.GREEN}{line}{Colors.RESET}")
                            elif line.startswith("-") and not line.startswith("---"):
                                print(f"{Colors.RED}{line}{Colors.RESET}")
                            else:
                                print(line)

                        ans = input(f"\nAplicar as correções acima em {file}? [y/N]: ").strip().lower()
                        if ans in ['y', 'yes']:
                            with open(file, "w", encoding="utf-8", errors="replace") as f:
                                f.write(fixed_content)
                            log("ANTIGRAVITY", f"Correções aplicadas em {file}.", Colors.GREEN)
                        else:
                            log("ANTIGRAVITY", f"Correções para {file} ignoradas pelo usuário.", Colors.YELLOW)

        if getattr(args, "json", False):
            print(json.dumps({"reports": reports}, indent=2, ensure_ascii=False))

        if is_staged and has_violations:
            print(f"{Colors.RED}❌ Auditoria barrada: Violações encontradas nos arquivos em stage.{Colors.RESET}")
            sys.exit(1)

    elif sub == "rules":
        mgr = get_rules_manager()
        rules_dir = mgr.resolve_rules_dir()
        rules_list = mgr.list_rules(rules_dir=rules_dir)
        role = getattr(args, "role", None)

        if role:
            rules_list = mgr.filter_rules_for_agent(role=role, rules=rules_list)

        as_json = getattr(args, "json", False)
        show_content = getattr(args, "content", False)

        if as_json:
            out = {
                "rules_directory": rules_dir,
                "rules": rules_list
            }
            if show_content:
                if role:
                    # Carrega tudo e depois filtra o texto
                    content = mgr.load_rules(rules_dir=rules_dir)
                    out["consolidated_content"] = mgr.filter_rules_for_agent(role=role, rules_text=content)
                else:
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
            if role:
                content = mgr.filter_rules_for_agent(role=role, rules_text=content)
            print("=" * 75)
            print(f"{Colors.BOLD}CONTEÚDO CONSOLIDADO DAS REGRAS:{Colors.RESET}")
            print("=" * 75)
            print(content)
            print("=" * 75 + "\n")

    elif sub in ["run", "eval"]:
        from core.logger import log_error

        def _resolve_text_or_file(val: Optional[str]) -> Optional[str]:
            import os
            if val and os.path.isfile(val):
                with open(val, "r", encoding="utf-8", errors="replace") as f:
                    return f.read().strip()
            return val

        prompt_text = _resolve_text_or_file(getattr(args, "prompt", ""))
        system_text = _resolve_text_or_file(getattr(args, "system", None))

        if not prompt_text:
            log_error("ANTIGRAVITY", "Nenhum prompt fornecido. Use: amb agy run 'Seu prompt' ou passe o caminho para um arquivo.")
            return

        model_override = getattr(args, "model", None)
        temp = getattr(args, "temperature", 0.2)
        client = AntigravityClient(model=model_override)
        out_f = getattr(args, "output", None)
        stream_flag = getattr(args, "stream", False)

        log("ANTIGRAVITY", f"Executando inferência com {client.model}...", Colors.CYAN)

        if stream_flag:
            import sys
            chunks = []
            for chunk in client.generate_text_stream(
                prompt=prompt_text,
                system_instruction=system_text,
                temperature=temp
            ):
                chunks.append(chunk)
                if not out_f:
                    sys.stdout.write(chunk)
                    sys.stdout.flush()

            if not out_f:
                print()  # Quebra de linha final

            res = "".join(chunks)
        else:
            res = client.generate_text(
                prompt=prompt_text,
                system_instruction=system_text,
                temperature=temp
            )

        if out_f:
            with open(out_f, "w", encoding="utf-8") as f:
                f.write(res)
            log("ANTIGRAVITY", f"Resposta salva em {out_f}", Colors.GREEN)
        elif not stream_flag:
            print(res)

    else:
        print("Subcomando do Antigravity inválido. Use 'amb agy --help'.")
