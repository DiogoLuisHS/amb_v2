import os
from typing import Dict, Any, Optional

from config import Colors, log, require_env, ApiExecutionError

def download_assets_core(client: Any, output_dir: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    """Baixa todas as telas e assets do projeto Stitch para um diretório local."""
    proj_id = project_id or client.project_id or require_env("STITCH_PROJECT_ID")
    payload = {
        "projectId": proj_id,
        "outputDir": os.path.abspath(output_dir)
    }
    log("STITCH", f"Baixando telas e assets do projeto {proj_id} para {output_dir}...", Colors.CYAN)
    return client._run_node_command("download_assets", payload)

def upload_asset_core(client: Any, file_path: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    """Faz upload de asset visual ou documento (PNG, JPG, WEBP, HTML) para o projeto Stitch."""
    proj_id = project_id or client.project_id or require_env("STITCH_PROJECT_ID")
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        raise ApiExecutionError(f"Arquivo não encontrado para upload: {abs_path}")
    payload = {
        "projectId": proj_id,
        "filePath": abs_path
    }
    log("STITCH", f"Enviando asset {os.path.basename(abs_path)} para o projeto {proj_id}...", Colors.CYAN)
    return client._run_node_command("upload_asset", payload)


def save_screen_html_core(screen_data: Dict[str, Any], output_path: str) -> str:
    """Salva o DOM HTML extraído da tela em um arquivo local."""
    html_code = screen_data.get("htmlCode", "")
    if not html_code:
        for msg in screen_data.get("messages", []):
            if "<html" in msg or "<div" in msg:
                html_code = msg
                break

    out_abs = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)
    with open(out_abs, "w", encoding="utf-8") as f:
        f.write(html_code or "<!-- Nenhum código HTML extraído do Stitch -->\n")
    log("STITCH", f"Código HTML salvo em: {out_abs}", Colors.GREEN)
    return out_abs

