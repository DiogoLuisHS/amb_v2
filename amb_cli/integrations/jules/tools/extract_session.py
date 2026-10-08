from pathlib import Path
from core.exceptions import AmbError
from integrations.jules.jules_client import JulesClient
from integrations.jules.jules_core.session_extractor import SessionExtractor
from core import Colors, log_error

from typing import Optional

def run_extract_session(
    session_id: str,
    dest: Optional[str] = None,
    apply: bool = False,
    show_bash: bool = False,
    client: Optional[JulesClient] = None
):
    try:
        if not client:
            client = JulesClient()
        sid = client.normalize_session_id(session_id)
        print(f"\n{Colors.BOLD}{Colors.CYAN}📥 EXTRAÇÃO DE SESSÃO DO JULES{Colors.RESET}")

        if show_bash:
            activities = client.list_activities(sid)
            bash_list = SessionExtractor.extract_bash_outputs(activities)

            print(f"\n=== 🖥️ COMANDOS BASH EXECUTADOS NA VM ===")
            if not bash_list:
                print("Nenhum comando bash registrado nos artefatos desta sessão.")
            else:
                for b in bash_list:
                    cmd = b.get("command", "")
                    exit_code = b.get("exitCode", 0)
                    out = b.get("output", "")

                    color = Colors.GREEN if exit_code == 0 else Colors.RED
                    print(f"{color}[$] {cmd}{Colors.RESET}")
                    print(f"    Status: exit {exit_code}")
                    print(f"    Saída:\n{out}")
        print(f"Buscando payload da sessão: {sid}...")

        session_data = client.get_session(sid)
        patch = SessionExtractor.extract_patch(session_data)
        lines = len(patch.splitlines())

        dest_path = Path(dest) if dest else Path(f".amb/patches/session_{sid}.patch")
        SessionExtractor.save_patch(patch, dest_path)

        print(f"✅ {Colors.GREEN}Patch salvo com sucesso!{Colors.RESET}")
        print(f"📁 Destino: {dest_path.absolute()}")
        print(f"📄 Tamanho: {lines} linhas")

        suggested_msg = SessionExtractor.extract_commit_message(session_data)
        if suggested_msg:
            print(f"  • Commit sugerido: \"{suggested_msg}\"")

        if apply:
            print(f"\n{Colors.YELLOW}Aplicando patch no workspace local...{Colors.RESET}")
            success, msg = SessionExtractor.apply_patch(patch, Path.cwd())
            if success:
                print(f"✅ {Colors.GREEN}{msg}{Colors.RESET}")
            else:
                log_error("GIT", msg)

    except AmbError as e:
        log_error("JULES", str(e))
    except Exception as e:
        log_error("JULES", f"Erro inesperado: {str(e)}")
