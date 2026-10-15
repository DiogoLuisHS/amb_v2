import os
import sys
import webbrowser
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

class AMBWebUIHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Mute simple HTTP requests for a cleaner console
        pass

def start_web_server(port: int = 8080, open_browser: bool = True) -> None:
    """
    Inicia um servidor web local leve e abre a interface web do AMB GUI no navegador.
    """
    web_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_dir)

    server_address = ('', port)

    try:
        httpd = HTTPServer(server_address, AMBWebUIHandler)
    except OSError as e:
        if e.errno == 98: # Address already in use
            print(f"[*] Porta {port} já está em uso, tentando {port + 1}...")
            start_web_server(port + 1, open_browser)
            return
        else:
            raise

    url = f"http://localhost:{port}"
    print(f"\n🚀 AMB_V2 Web Console iniciado na porta {port}")
    print(f"🔗 Acesse: {url}\n")
    print("Pressione Ctrl+C para encerrar o servidor.")

    if open_browser:
        # Start browser opening in a short thread to ensure server is ready
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Encerrando servidor web do AMB GUI...")
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":
    start_web_server()
