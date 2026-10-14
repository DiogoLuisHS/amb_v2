import os
import json
import webbrowser
from typing import Any
from core.bootstrap import ensure_amb_env

ensure_amb_env()

def handle_cmd_stitch(args: Any) -> None:
    """Implementação isolada do comando stitch."""
    sub = getattr(args, "stitch_cmd", None)
    if not sub:
        sub = "list"
    from integrations.stitch.stitch_client import StitchClient
    from core import Colors, log

    client = StitchClient()

    def _resolve_prompt(p: str) -> str:
        if p and os.path.exists(p) and os.path.isfile(p):
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                return f.read().strip()
        return p

    def _open_in_browser(res: dict, output_file: str = None) -> None:
        url = res.get("screenshotUrl")
        if output_file and os.path.exists(output_file):
            webbrowser.open(f"file://{os.path.abspath(output_file)}")
        elif url:
            webbrowser.open(url)

    as_json = getattr(args, "json", False)

    if sub == "list":
        screens = client.list_screens(project_id=getattr(args, "project_id", None))
        if as_json:
            print(json.dumps(screens, indent=2, ensure_ascii=False))
            return
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== TELAS DO PROJETO STITCH ({len(screens)} encontrada(s)) ==={Colors.RESET}\n")
        if not screens:
            print("  Nenhuma tela encontrada no projeto ativo.")
            return
        for s in screens:
            sid = s.get("id") or s.get("screenId") or (s.get("name", "").split("/")[-1])
            title = s.get("title") or s.get("label") or "Sem título"
            dims = f" ({s.get('width')}x{s.get('height')})" if s.get("width") and s.get("height") else ""
            desc = f" - {s.get('description')}" if s.get("description") else ""
            print(f"  • {Colors.GREEN}{sid:<14}{Colors.RESET} {Colors.BOLD}{title}{Colors.RESET}{dims}{desc}")
        print()

    elif sub == "view":
        sid = getattr(args, "screen_id", None)
        if not sid:
            from core import log_error
            log_error("O ID da tela é obrigatório. Ex: amb stitch view <id>")
            return
        res = client.get_screen(screen_id=sid)
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        log("STITCH", f"Abrindo visualização da tela {sid}...", Colors.GREEN)
        _open_in_browser(res)

    elif sub == "generate":
        raw_prompt = getattr(args, "prompt", None) or getattr(args, "prompt_flag", None)
        if not raw_prompt:
            from core import log_error
            log_error("O argumento posicional 'prompt' ou a flag '--prompt' são obrigatórios.")
            return

        prompt_text = _resolve_prompt(raw_prompt)
        device = getattr(args, "device", None)
        output_file = getattr(args, "output", None)
        res = client.generate_screen(prompt=prompt_text, device_type=device, output_file=output_file)
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        sid = res.get("screenId") or "N/A"
        log("STITCH", f"Tela gerada com sucesso! ID: {sid}", Colors.GREEN)
        if res.get("screenshotUrl"):
            print(f"  • Screenshot: {res['screenshotUrl']}")
        if output_file:
            print(f"  • HTML salvo em: {output_file}")

        if getattr(args, "open", False):
            _open_in_browser(res, output_file)

    elif sub == "refine":
        sid = getattr(args, "screen_id", None) or getattr(args, "screen_id_flag", None)
        raw_prompt = getattr(args, "prompt", None) or getattr(args, "prompt_flag", None)

        if not sid or not raw_prompt:
            from core import log_error
            log_error("O ID da tela e o prompt são obrigatórios para refinamento. Ex: amb stitch refine <id> \"<prompt>\"")
            return

        prompt_text = _resolve_prompt(raw_prompt)
        output_file = getattr(args, "output", None)
        device = getattr(args, "device", None)
        res = client.edit_screen(screen_id=sid, prompt=prompt_text, device_type=device, output_file=output_file)
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        log("STITCH", f"Tela {sid} refinada com sucesso!", Colors.GREEN)
        if res.get("screenshotUrl"):
            print(f"  • Nova Screenshot: {res['screenshotUrl']}")
        if output_file:
            print(f"  • HTML salvo em: {output_file}")

        if getattr(args, "open", False):
            _open_in_browser(res, output_file)

    elif sub == "get":
        sid = getattr(args, "screen_id", None) or getattr(args, "screen_id_flag", None)

        if not sid:
            from core import log_error
            log_error("O ID da tela é obrigatório. Ex: amb stitch get <id>")
            return

        output_file = getattr(args, "output", None)
        res = client.get_screen(screen_id=sid, output_file=output_file)
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        log("STITCH", f"Detalhes da tela {sid} obtidos com sucesso.", Colors.GREEN)
        if res.get("title"):
            print(f"  • Título: {res['title']}")
        if res.get("screenshotUrl"):
            print(f"  • Screenshot: {res['screenshotUrl']}")
        if res.get("htmlCode"):
            print(f"  • DOM HTML: {len(res['htmlCode'])} caracteres")
        if output_file:
            print(f"  • HTML salvo em: {output_file}")

        if getattr(args, "open", False):
            _open_in_browser(res, output_file)

    elif sub == "variants":
        device = getattr(args, "device", None)
        res = client.generate_variants(screen_id=args.screen_id, prompt=args.prompt, variant_count=args.count, device_type=device)
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        log("STITCH", f"Variantes geradas com sucesso! ID: {res.get('screenId')}", Colors.GREEN)
        if res.get("screenshotUrl"):
            print(f"  • Screenshot: {res['screenshotUrl']}")

    elif sub == "download":
        out_dir = getattr(args, "output", "./stitch_assets")
        pid = getattr(args, "project_id", None)
        res = client.download_assets(output_dir=out_dir, project_id=pid)
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        log("STITCH", f"Assets baixados com sucesso para: {out_dir}", Colors.GREEN)

    elif sub == "project":
        pid = getattr(args, "project_id", None)
        res = client.get_project(project_id=pid)
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== PROJETO STITCH ==={Colors.RESET}\n")
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif sub == "sync":
        res = client.sync_design_system(design_md_path=getattr(args, "file", None))
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        log("STITCH", "✅ Design System sincronizado com sucesso!", Colors.GREEN)

    elif sub in ["status", "check"]:
        res = client.get_status()
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return

        print(f"\n{Colors.BOLD}{Colors.CYAN}=== 🎨 DIAGNÓSTICO GOOGLE STITCH SDK ==={Colors.RESET}")

        # Node
        n_ok = res["node_runtime"]["installed"]
        n_ver = res["node_runtime"]["version"]
        n_str = f"Instalado ({n_ver})" if n_ok else f"{Colors.RED}Não encontrado{Colors.RESET}"
        print(f"  • Node.js Runtime:   {n_str}")

        # API Key
        k_ok = res["api_key"]["configured"]
        k_str = "Configurada" if k_ok else f"{Colors.RED}Ausente{Colors.RESET}"
        print(f"  • API Key:           {k_str}")

        # Runner
        r_ok = res["runner"]["installed"]
        r_str = "Instalado" if r_ok else f"{Colors.RED}Não encontrado{Colors.RESET}"
        print(f"  • Runner SDK:        {r_str}")

        # Project
        p_ok = res["project_id"]["configured"]
        p_val = res["project_id"].get("value")
        p_str = f"projects/{p_val}" if p_ok else f"{Colors.RED}Ausente{Colors.RESET}"
        print(f"  • Projeto Ativo:     {p_str}")

        # Connectivity
        c_ok = res["connectivity"]["connected"]
        c_det = res["connectivity"].get("details", "")
        c_str = f"Conectada ({c_det})" if c_ok else f"{Colors.RED}Desconectada ({c_det}){Colors.RESET}"
        if not (n_ok and k_ok and p_ok and r_ok):
             c_str = f"{Colors.YELLOW}Ignorada (dependências faltantes){Colors.RESET}"
        print(f"  • Conectividade:     {c_str}\n")

    elif sub == "call":
        payload_str = getattr(args, "payload", "{}")
        if os.path.exists(payload_str) and os.path.isfile(payload_str):
            with open(payload_str, "r", encoding="utf-8", errors="replace") as pf:
                payload = json.load(pf)
        else:
            payload = json.loads(payload_str)
        res = client.call_tool(args.tool, payload)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    else:
        print("Subcomando do Stitch inválido. Use 'amb stitch --help'.")
