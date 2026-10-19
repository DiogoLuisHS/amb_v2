"""Módulo de Servidor Web Leve para o AMB GUI."""
import http.server
import socketserver
import socket
import webbrowser
import os
import threading
import json
import urllib.parse
from pathlib import Path
from typing import Optional, Any

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

class WebConsoleHandler(http.server.SimpleHTTPRequestHandler):
    """Handler HTTP customizado com suporte a rotas de API da interface."""

    def do_GET(self) -> None:
        if self.path.startswith('/api/exec'):
            parsed_path = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed_path.query)
            cmd = query.get('cmd', [''])[0]

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            response = {
                "status": "ok",
                "output": f"Mock execution of '{cmd}' completed."
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return

        super().do_GET()

def start_web_gui(headless: bool = False, port: Optional[int] = None, run_forever: bool = True) -> None:
    """Inicia o servidor web local para servir a interface HTML/JS/CSS e abre no navegador."""
    web_dir = Path(__file__).parent.resolve()
    original_cwd = os.getcwd()
    os.chdir(web_dir)

    selected_port = port if port is not None else get_free_port(8080)

    class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        daemon_threads = True
        allow_reuse_address = True

    try:
        httpd = ThreadedHTTPServer(("localhost", selected_port), WebConsoleHandler)
    except OSError as e:
        os.chdir(original_cwd)
        raise RuntimeError(f"Falha ao iniciar o servidor web na porta {selected_port}: {e}")

    server_url = f"http://localhost:{selected_port}"
    print(f"\n🚀 AMB Web Console inicializado!")
    print(f"🔗 Servidor rodando em: {server_url}")
    print(f"📂 Diretório servido: {web_dir}")
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
        os.chdir(original_cwd)

if __name__ == "__main__":
    start_web_gui()
