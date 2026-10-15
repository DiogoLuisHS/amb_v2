"""Módulo de Servidor Web Leve para o AMB GUI."""
import http.server
import socketserver
import socket
import webbrowser
import os
import threading
from pathlib import Path
from typing import Optional

def get_free_port(start_port: int = 8080) -> int:
    """Encontra uma porta livre a partir da start_port. Se start_port estiver ocupada, tenta até achar uma."""
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                port += 1

def start_web_gui(headless: bool = False, port: Optional[int] = None, run_forever: bool = True) -> None:
    """
    Inicia o servidor web local para servir a interface HTML/JS/CSS e abre no navegador.

    Args:
        headless (bool): Se True, não tenta abrir o navegador automaticamente.
        port (int): Porta para rodar o servidor. Se None, procura uma livre.
    """
    web_dir = Path(__file__).parent.resolve()

    # Muda o diretório atual para a pasta web para o SimpleHTTPRequestHandler servir daqui
    original_cwd = os.getcwd()
    os.chdir(web_dir)

    selected_port = port if port is not None else get_free_port(8080)

    Handler = http.server.SimpleHTTPRequestHandler

    # Usar ThreadingMixIn para não bloquear a thread principal, caso queiramos adicionar mais lógica
    class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        daemon_threads = True
        allow_reuse_address = True

    try:
        httpd = ThreadedHTTPServer(("localhost", selected_port), Handler)
    except OSError as e:
        os.chdir(original_cwd)
        raise RuntimeError(f"Falha ao iniciar o servidor web na porta {selected_port}: {e}")

    server_url = f"http://localhost:{selected_port}"
    print(f"\n🚀 AMB Web Console inicializado!")
    print(f"🔗 Servidor rodando em: {server_url}")
    print(f"📂 Diretório servido: {web_dir}")
    print("Pressione Ctrl+C para encerrar.\n")

    if not headless:
        # Tenta abrir o navegador em uma thread separada para não atrasar a inicialização do servidor
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
            httpd.handle_request() # Handles a single request and returns (used in tests)
    except KeyboardInterrupt:
        print("\n⏹️ Encerrando servidor web...")
    finally:
        httpd.server_close()
        os.chdir(original_cwd)

if __name__ == "__main__":
    start_web_gui()
