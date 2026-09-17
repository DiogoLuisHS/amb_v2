import os
import json
from typing import Any
from config.bootstrap import ensure_amb_env

ensure_amb_env()

def handle_cmd_stitch(args: Any) -> None:
    """Implementação isolada do comando stitch."""
    sub = args.stitch_cmd
    from integrations.stitch.stitch_client import StitchClient
    from config import Colors, log

    client = StitchClient()

    def _resolve_prompt(p: str) -> str:
        if p and os.path.exists(p) and os.path.isfile(p):
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                return f.read().strip()
        return p

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

    elif sub == "generate":
        prompt_text = _resolve_prompt(args.prompt)
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

    elif sub == "refine":
        prompt_text = _resolve_prompt(args.prompt)
        output_file = getattr(args, "output", None)
        device = getattr(args, "device", None)
        res = client.edit_screen(screen_id=args.screen_id, prompt=prompt_text, device_type=device, output_file=output_file)
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        log("STITCH", f"Tela {args.screen_id} refinada com sucesso!", Colors.GREEN)
        if res.get("screenshotUrl"):
            print(f"  • Nova Screenshot: {res['screenshotUrl']}")
        if output_file:
            print(f"  • HTML salvo em: {output_file}")

    elif sub == "get":
        output_file = getattr(args, "output", None)
        res = client.get_screen(screen_id=args.screen_id, output_file=output_file)
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        log("STITCH", f"Detalhes da tela {args.screen_id} obtidos com sucesso.", Colors.GREEN)
        if res.get("title"):
            print(f"  • Título: {res['title']}")
        if res.get("screenshotUrl"):
            print(f"  • Screenshot: {res['screenshotUrl']}")
        if res.get("htmlCode"):
            print(f"  • DOM HTML: {len(res['htmlCode'])} caracteres")
        if output_file:
            print(f"  • HTML salvo em: {output_file}")

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
