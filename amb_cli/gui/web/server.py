"""Módulo de Servidor Web Leve para o AMB GUI."""
import http.server
import socketserver
import socket
import webbrowser
import os
import threading
import json
import urllib.parse
import subprocess
import functools
from pathlib import Path
from typing import Optional, Dict, Any, List

from amb_cli.core.env import load_env_file, get_env
from amb_cli.core.config_manager import ConfigManager


def get_free_port(start_port: int = 8080) -> int:
    """Encontra uma porta livre a partir da start_port."""
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                port += 1


def get_project_status(project_root: Path) -> Dict[str, Any]:
    """Coleta informações em tempo real do projeto respeitando o .env e Git."""
    env_file = project_root / ".env"
    if env_file.exists():
        load_env_file(path=str(env_file))
    try:
        ConfigManager.get_instance().reload()
    except Exception:
        pass

    branch = "unknown"
    git_clean = True
    repo_name = project_root.name

    try:
        res = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=3,
            encoding="utf-8",
            errors="replace"
        )
        if res.returncode == 0 and res.stdout.strip():
            branch = res.stdout.strip()
    except Exception:
        pass

    try:
        res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=3,
            encoding="utf-8",
            errors="replace"
        )
        if res.returncode == 0:
            git_clean = (len(res.stdout.strip()) == 0)
    except Exception:
        pass

    cfg_repo = os.environ.get("GITHUB_REPOSITORY") or get_env("GITHUB_REPOSITORY")
    if cfg_repo:
        repo_name = cfg_repo

    model_name = "gemini-3.8-flash"
    model_source = "padrão (default)"
    if os.environ.get("ANTIGRAVITY_MODEL"):
        model_name = os.environ["ANTIGRAVITY_MODEL"]
        model_source = ".env (ANTIGRAVITY_MODEL)"
    elif os.environ.get("GEMINI_MODEL"):
        model_name = os.environ["GEMINI_MODEL"]
        model_source = ".env (GEMINI_MODEL)"
    else:
        p_file = project_root / ".amb" / "amb_project.json"
        if not p_file.exists():
            p_file = project_root / "amb_project.json"
        if p_file.exists():
            try:
                with open(p_file, "r", encoding="utf-8", errors="replace") as pf:
                    p_data = json.load(pf)
                    if isinstance(p_data, dict):
                        if p_data.get("antigravity", {}).get("model"):
                            model_name = p_data["antigravity"]["model"]
                            model_source = "amb_project.json"
                        elif p_data.get("gemini", {}).get("model"):
                            model_name = p_data["gemini"]["model"]
                            model_source = "amb_project.json"
            except Exception:
                pass

    apis = {
        "gemini": bool(os.environ.get("GEMINI_API_KEY") or get_env("GEMINI_API_KEY")),
        "jules": bool(os.environ.get("JULES_API_KEY") or get_env("JULES_API_KEY")),
        "stitch": bool(os.environ.get("STITCH_API_KEY") or get_env("STITCH_API_KEY")),
        "github": bool(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or get_env("GITHUB_TOKEN")),
    }

    loop_info = {
        "state": "IDLE",
        "current_cycle": 0,
        "total_cycles": 0,
        "active_item": None,
        "session_id": None,
        "updated_at": None,
    }
    loop_file = project_root / ".amb" / "loop_state.json"
    if loop_file.exists():
        try:
            with open(loop_file, "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)
                loop_info["state"] = data.get("state", "IDLE")
                loop_info["current_cycle"] = data.get("current_cycle", 0)
                loop_info["total_cycles"] = data.get("total_cycles", 0)
                loop_info["active_item"] = data.get("active_item")
                loop_info["session_id"] = data.get("session_id")
                loop_info["updated_at"] = data.get("updated_at")
        except Exception:
            pass

    sessions: List[Dict[str, Any]] = []
    telemetry_file = project_root / ".amb" / "telemetry.jsonl"
    if telemetry_file.exists():
        try:
            with open(telemetry_file, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                for line in reversed(lines[-10:]):
                    if line.strip():
                        rec = json.loads(line)
                        sessions.append({
                            "id": rec.get("session_id") or rec.get("id") or "#telemetry",
                            "name": rec.get("event") or rec.get("task") or "Operação AMB",
                            "module": rec.get("module") or "core",
                            "status": rec.get("status", "COMPLETED"),
                            "branch": branch,
                            "duration": rec.get("duration", "N/A"),
                        })
        except Exception:
            pass

    return {
        "project": {
            "name": repo_name,
            "root": str(project_root),
            "branch": branch,
            "git_clean": git_clean,
        },
        "model": {
            "name": model_name,
            "source": model_source,
        },
        "apis": apis,
        "loop_state": loop_info,
        "sessions": sessions,
    }


class WebConsoleHandler(http.server.SimpleHTTPRequestHandler):
    """Handler HTTP com suporte a rotas de status e execução de comandos reais."""

    def do_GET(self) -> None:
        project_root = getattr(self.server, "project_root", Path.cwd())

        if self.path.startswith('/api/status'):
            status_data = get_project_status(project_root)
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(status_data, ensure_ascii=False).encode("utf-8"))
            return

        if self.path.startswith('/api/exec'):
            parsed_path = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed_path.query)
            cmd = query.get('cmd', [''])[0].strip()

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()

            if not cmd:
                response = {"status": "error", "output": "Nenhum comando fornecido."}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
                return

            # Validação de segurança: apenas comandos do ecossistema amb / git / pytest
            allowed_prefixes = ("amb ", "git ", "pytest", "python -m py_compile")
            if not any(cmd.startswith(prefix) for prefix in allowed_prefixes):
                response = {
                    "status": "error",
                    "output": f"Comando '{cmd}' não permitido por diretrizes de segurança da interface."
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
                return

            try:
                proc = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=str(project_root),
                    capture_output=True,
                    text=True,
                    timeout=60,
                    encoding="utf-8",
                    errors="replace"
                )
                output = proc.stdout if proc.returncode == 0 else (proc.stderr or proc.stdout)
                output = output.strip() or f"Comando '{cmd}' concluído (código {proc.returncode})."
                response = {
                    "status": "ok" if proc.returncode == 0 else "error",
                    "exit_code": proc.returncode,
                    "output": output
                }
            except subprocess.TimeoutExpired:
                response = {"status": "error", "output": f"Timeout ao executar comando '{cmd}' (limite 60s)."}
            except Exception as e:
                response = {"status": "error", "output": f"Erro de execução: {e}"}

            self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
            return

        super().do_GET()


class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True
    project_root: Path = Path.cwd()


def start_web_gui(headless: bool = False, port: Optional[int] = None, run_forever: bool = True) -> None:
    """Inicia o servidor web local servindo a pasta web sem alterar o diretório de trabalho do projeto."""
    project_root = Path.cwd().resolve()
    web_dir = Path(__file__).parent.resolve()
    selected_port = port if port is not None else get_free_port(8080)

    handler = functools.partial(WebConsoleHandler, directory=str(web_dir))

    try:
        httpd = ThreadedHTTPServer(("localhost", selected_port), handler)
        httpd.project_root = project_root
    except OSError as e:
        raise RuntimeError(f"Falha ao iniciar o servidor web na porta {selected_port}: {e}")

    server_url = f"http://localhost:{selected_port}"
    print(f"\n🚀 AMB Web Console inicializado!")
    print(f"🔗 Servidor rodando em: {server_url}")
    print(f"📁 Projeto monitorado: {project_root}")
    print("Pressione Ctrl+C para encerrar.\n")

    if not headless:
        def open_browser():
            try:
                webbrowser.open(server_url)
            except Exception as e:
                print(f"[Aviso] Não foi possível abrir o navegador automaticamente: {e}")

        threading.Thread(target=open_browser, daemon=True).start()

    try:
        if run_forever:
            httpd.serve_forever()
        else:
            httpd.handle_request()
    except KeyboardInterrupt:
        print("\n⏹️ Encerrando servidor web...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    start_web_gui()
