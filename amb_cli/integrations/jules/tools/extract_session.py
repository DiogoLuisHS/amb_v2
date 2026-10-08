from pathlib import Path
from core.exceptions import AmbError
from integrations.jules.jules_client import JulesClient
from integrations.jules.jules_core.session_extractor import SessionExtractor
from core import Colors, log_error

def run_extract_session(session_id: str, dest: str = None, apply: bool = False):
    try:
        client = JulesClient()
        sid = client.normalize_session_id(session_id)
        print(f"\n{Colors.BOLD}{Colors.CYAN}📥 EXTRAÇÃO DE SESSÃO DO JULES{Colors.RESET}")
        print(f"Buscando payload da sessão: {sid}...")

        session_data = client.get_session(sid)
        patch = SessionExtractor.extract_patch(session_data)
        lines = len(patch.splitlines())

        dest_path = Path(dest) if dest else Path(f".amb/patches/session_{sid}.patch")
        SessionExtractor.save_patch(patch, dest_path)

        print(f"✅ {Colors.GREEN}Patch salvo com sucesso!{Colors.RESET}")
        print(f"📁 Destino: {dest_path.absolute()}")
        print(f"📄 Tamanho: {lines} linhas")

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
