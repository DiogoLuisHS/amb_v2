import sys
import http.server
import socketserver
import webbrowser
import os
import threading
import json
import urllib.parse
from typing import Any

class MockAPIHandler(http.server.SimpleHTTPRequestHandler):
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
            self.wfile.write(json.dumps(response).encode())
            return

        super().do_GET()

def start_web_gui() -> None:
    PORT: int = 8080
    DIRECTORY: str = os.path.dirname(os.path.abspath(__file__))

    class Handler(MockAPIHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=DIRECTORY, **kwargs)

    # Try finding an open port
    httpd: Any = None
    while PORT < 8090:
        try:
            httpd = socketserver.TCPServer(("", PORT), Handler)
            break
        except OSError:
            PORT += 1

    if httpd is None:
        print("Erro: Não foi possível encontrar uma porta disponível.")
        return

    url: str = f"http://localhost:{PORT}"
    print(f"🚀 Iniciando AMB Web Console em {url}...")

    def open_browser() -> None:
        try:
            # Fallback for headless environments
            if os.environ.get('DISPLAY') or sys.platform == 'win32' or sys.platform == 'darwin':
                 webbrowser.open(url)
        except Exception as e:
            print(f"Aviso: Não foi possível abrir o navegador ({e}). O servidor continua rodando.")

    thread = threading.Thread(target=open_browser)
    thread.daemon = True
    thread.start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDesligando AMB Web Console.")
        httpd.server_close()
