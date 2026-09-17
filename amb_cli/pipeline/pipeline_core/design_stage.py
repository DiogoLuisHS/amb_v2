import json
from typing import Optional, Dict, Any
from config import Colors, log, get_device_type
from integrations.stitch.stitch_client import generate_screen, get_screen, edit_screen, generate_variants, sync_design_system

def process_design_stage(
    stitch_prompt: str,
    current_screen_id: Optional[str],
    edit_screen_id: Optional[str],
    device_type: Optional[str],
    auto_approve: bool,
    sync_ds: bool
) -> Dict[str, Any]:

    if sync_ds:
        log("ETAPA 1.1", "🎨 Sincronizando Design Tokens locais com o Stitch...", Colors.HEADER)
        try:
            sync_design_system()
        except Exception as e:
            from config import log_error
            log_error("SYNC-DS", f"Aviso na sincronização de tokens: {e}")

    log("ETAPA 2/6", "🎨 Processando Layout Visual no Stitch SDK...", Colors.HEADER)

    if current_screen_id and not edit_screen_id:
        log("STITCH", f"Buscando tela existente ID: {current_screen_id}...", Colors.CYAN)
        screen_data = get_screen(screen_id=current_screen_id)
    elif edit_screen_id:
        log("STITCH", f"Refinando tela ID {edit_screen_id} com novo prompt...", Colors.CYAN)
        screen_data = edit_screen(screen_id=edit_screen_id, prompt=stitch_prompt)
    else:
        target_dev = device_type or get_device_type()
        dev_label = f" ({target_dev})" if target_dev else ""
        log("STITCH", f"Disparando geração de nova tela visual{dev_label}...", Colors.CYAN)
        screen_data = generate_screen(prompt=stitch_prompt, device_type=target_dev)

    current_screen_id = screen_data.get("screenId") or current_screen_id
    stitch_html = screen_data.get("htmlCode", "")
    screenshot_url = screen_data.get("screenshotUrl", "")
    screen_title = screen_data.get("title", "")

    print("\n" + "-" * 75)
    print(f"✨ {Colors.BOLD}Mockup Stitch Gerado com Sucesso!{Colors.RESET}")
    print(f"🆔 Screen ID: {Colors.GREEN}{current_screen_id}{Colors.RESET}")
    if screen_title:
        print(f"🏷️ Título: {screen_title}")
    if screenshot_url:
        print(f"🖼️ Screenshot: {Colors.BLUE}{screenshot_url}{Colors.RESET}")
    print(f"📦 DOM HTML Extraído: {len(stitch_html)} caracteres")
    print("-" * 75 + "\n")

    cancelled = False

    if not auto_approve:
        log("ETAPA 3/6", "🚪 Gatekeeper 1: Decisão de Design e Layout", Colors.HEADER)
        print("Escolha a próxima ação:")
        print("  [1] Aprovar mockup e seguir para Síntese Cognitiva & Jules (Recomendado)")
        print("  [2] Refinar visual com nova instrução no Stitch")
        print("  [3] Gerar 3 variantes de design alternativas")
        print("  [4] Cancelar execução")

        try:
            choice = input(f"\n{Colors.BOLD}Opção [1-4] (Padrão: 1): {Colors.RESET}").strip() or "1"
        except (EOFError, KeyboardInterrupt):
            choice = "1"

        if choice == "2":
            instruction = input(f"{Colors.BOLD}Digite a instrução de refinamento: {Colors.RESET}").strip()
            if instruction:
                log("STITCH", f"Refinando tela {current_screen_id}...", Colors.CYAN)
                screen_data = edit_screen(screen_id=current_screen_id, prompt=instruction)
                stitch_html = screen_data.get("htmlCode", "")
                screenshot_url = screen_data.get("screenshotUrl", "")
                print(f"✅ Refinamento concluído. Nova screenshot: {screenshot_url}")
        elif choice == "3":
            log("STITCH", f"Gerando variantes para a tela {current_screen_id}...", Colors.CYAN)
            vars_data = generate_variants(screen_id=current_screen_id, count=3)
            print(f"✅ Variantes geradas: {json.dumps(vars_data, indent=2)}")
        elif choice == "4":
            print(f"{Colors.YELLOW}Execução cancelada pelo usuário.{Colors.RESET}")
            cancelled = True

    return {
        "current_screen_id": current_screen_id,
        "stitch_html": stitch_html,
        "screenshot_url": screenshot_url,
        "screen_title": screen_title,
        "cancelled": cancelled
    }
