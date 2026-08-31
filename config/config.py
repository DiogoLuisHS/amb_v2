#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚙️ AMB_V2 - Utilitário Central de Configuração, Logging e Fail-Fast (SRP)
Responsabilidade Única: Carregar variáveis, validar requisitos estritos e fornecer
diagnósticos imediatos sem mascaramento de falhas.
"""

import os
import sys
import json
from datetime import datetime
from typing import Any, Optional

# Garante suporte adequado a UTF-8 no terminal Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class Colors:
    """Paleta ANSI para logs padronizados no terminal."""
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


class AmbError(Exception):
    """Exceção base para o ecossistema amb_v2 com diagnóstico detalhado."""
    def __init__(self, message: str, hint: Optional[str] = None):
        full_msg = f"{message}"
        if hint:
            full_msg += f"\n👉 COMO RESOLVER: {hint}"
        super().__init__(full_msg)
        self.message = message
        self.hint = hint


class ConfigurationError(AmbError):
    """Lançado quando uma chave de API, arquivo ou configuração mandatória está ausente."""
    pass


class ApiExecutionError(AmbError):
    """Lançado quando uma chamada a uma das SDKs/APIs falha explicitamente."""
    pass


def log(tag: str, message: str, color: str = Colors.RESET) -> None:
    """Imprime mensagem com timestamp e tag colorida."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{color}{Colors.BOLD}{tag}{Colors.RESET}] {message}", flush=True)


def log_error(tag: str, message: str, hint: Optional[str] = None) -> None:
    """Imprime erro com formatação de alerta e dica de resolução."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{Colors.RED}{Colors.BOLD}ERRO::{tag}{Colors.RESET}] {message}", file=sys.stderr, flush=True)
    if hint:
        print(f"[{timestamp}] [{Colors.YELLOW}{Colors.BOLD}DICA DE RESOLUÇÃO{Colors.RESET}] {hint}", file=sys.stderr, flush=True)


def find_repo_root(start_dir: Optional[str] = None) -> str:
    """Localiza a raiz do repositório procurando por .git, .env ou package.json a partir do diretório atual.
    
    Regra de prioridade:
    1. Preferência por .git (marcador definitivo de raiz de repositório)
    2. .env como marcador de projeto configurado
    3. Quando rodando DENTRO do amb_v2 (modo standalone), retorna o próprio amb_v2
       e não sobe para o pai — a menos que o pai tenha .env (projeto hospedeiro)
    """
    start = os.path.abspath(start_dir or os.getcwd())
    curr = start

    # Sobe até 6 níveis procurando marcadores de repositório
    for _ in range(6):
        has_git = os.path.exists(os.path.join(curr, ".git"))
        has_env = os.path.exists(os.path.join(curr, ".env"))
        has_markers = (
            has_git
            or has_env
            or os.path.exists(os.path.join(curr, "amb_project.json"))
            or os.path.exists(os.path.join(curr, "package.json"))
            or os.path.exists(os.path.join(curr, "pyproject.toml"))
            or os.path.exists(os.path.join(curr, "requirements.txt"))
        )

        if has_markers:
            # Caso especial: estamos dentro do próprio amb_v2 (modo standalone / desenvolvimento)
            if os.path.basename(curr) == "amb_v2":
                parent = os.path.dirname(curr)
                parent_has_env = os.path.exists(os.path.join(parent, ".env"))
                parent_has_git = os.path.exists(os.path.join(parent, ".git"))
                # Só sobe para o pai se o pai tiver .env (projeto hospedeiro configurado)
                # .git no pai sem .env = outro repositório independente, não o projeto hospedeiro
                if parent_has_env:
                    return parent
                # amb_v2 tem seu próprio .env → retorna o próprio amb_v2
                if has_env:
                    return curr
                # amb_v2 sem .env: só sobe se o pai tiver .git E .env
                if parent_has_git and parent_has_env:
                    return parent
            return curr

        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent

    return start


def load_env_file() -> None:
    """Carrega variáveis do arquivo .env localizado na raiz do repositório."""
    root = find_repo_root()
    env_path = os.path.join(root, ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'").strip('"')
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception as e:
            log_error("CONFIG", f"Falha ao ler arquivo .env em {env_path}: {e}")


def load_project_json() -> dict:
    """Carrega dados contextuais de amb_project.json prioritariamente em .amb/, .jules/ ou na raiz."""
    root = find_repo_root()
    candidates = [
        os.path.join(root, ".amb", "amb_project.json"),
        os.path.join(root, ".amb", "project.json"),
        os.path.join(root, ".jules", "amb_project.json"),
        os.path.join(root, ".jules", "project.json"),
        os.path.join(root, "amb_project.json"),
        os.path.join(root, "amb_v2", "config", "amb_project.json"),
        os.path.join(os.path.dirname(__file__), "amb_project.json"),
    ]
    for p_path in candidates:
        if os.path.exists(p_path):
            try:
                with open(p_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {}


# Carrega variáveis automaticamente na importação
load_env_file()
_PROJECT_METADATA = load_project_json()


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Obtém variável de ambiente ou metadata de projeto, retornando default se não existir."""
    if key in os.environ and os.environ[key].strip():
        return os.environ[key].strip()
    if key in _PROJECT_METADATA and str(_PROJECT_METADATA[key]).strip():
        return str(_PROJECT_METADATA[key]).strip()
    return default


def require_env(key: str, hint: Optional[str] = None) -> str:
    """
    Exige a presença de uma variável de ambiente.
    Fail-Fast: Lança ConfigurationError imediatamente se ausente.
    """
    val = get_env(key)
    if not val:
        default_hints = {
            "STITCH_API_KEY": "Obtenha em https://stitch.withgoogle.com e adicione no arquivo .env (STITCH_API_KEY=...)",
            "STITCH_PROJECT_ID": "Informe via argumento CLI (--project-id) ou configure STITCH_PROJECT_ID no .env",
            "JULES_API_KEY": "Obtenha em https://jules.google.com e adicione no arquivo .env (JULES_API_KEY=...)",
            "GITHUB_REPOSITORY": "Configure GITHUB_REPOSITORY=usuario/repositorio no .env ou execute setup_project.py",
            "GEMINI_API_KEY": "Obtenha em https://aistudio.google.com/app/api-keys e adicione no .env (GEMINI_API_KEY=...)",
            "RENDER_API_KEY": "Obtenha em https://dashboard.render.com/u/settings#api-keys e adicione no .env (RENDER_API_KEY=...)",
        }
        resolved_hint = hint or default_hints.get(key, f"Defina a variável '{key}' no arquivo .env ou execute python amb_v2/config/setup_project.py")
        raise ConfigurationError(f"Variável mandatória ausente: '{key}'", hint=resolved_hint)
    return val


def get_repo_name() -> str:
    """Obtém o nome do repositório configurado no .env (GITHUB_REPOSITORY)."""
    repo = get_env("GITHUB_REPOSITORY")
    if repo:
        return repo
    p_meta = load_project_json()
    if "repository" in p_meta and p_meta["repository"]:
        return p_meta["repository"]
    raise ConfigurationError(
        "Variável GITHUB_REPOSITORY não configurada.",
        hint="Defina GITHUB_REPOSITORY=usuario/repo no seu arquivo .env"
    )


def main():
    """Valida e exibe o checklist visual de configurações do repositório ativo."""
    print(f"{Colors.BOLD}{Colors.CYAN}=== AMB_V2 - VALIDAÇÃO DE AMBIENTE E CONFIGURAÇÕES ==={Colors.RESET}\n")
    root = find_repo_root()
    p_json_exists = (
        os.path.exists(os.path.join(root, ".amb", "amb_project.json"))
        or os.path.exists(os.path.join(root, ".amb", "project.json"))
        or os.path.exists(os.path.join(root, ".jules", "amb_project.json"))
        or os.path.exists(os.path.join(root, ".jules", "project.json"))
        or os.path.exists(os.path.join(root, "amb_project.json"))
        or os.path.exists(os.path.join(root, "amb_v2", "config", "amb_project.json"))
        or os.path.exists(os.path.join(os.path.dirname(__file__), "amb_project.json"))
    )
    print(f"📁 Raiz do Projeto: {root}")
    print(f"📄 Arquivo .env: {'Encontrado' if os.path.exists(os.path.join(root, '.env')) else 'Não encontrado'}")
    print(f"📄 Arquivo .amb/amb_project.json: {'Encontrado' if p_json_exists else 'Não encontrado'}\n")

    keys_to_check = [
        ("STITCH_API_KEY", "Google Stitch SDK"),
        ("STITCH_PROJECT_ID", "Stitch Project ID"),
        ("JULES_API_KEY", "Google Jules SDK / API"),
        ("GITHUB_REPOSITORY", "Repositório GitHub"),
        ("GEMINI_API_KEY", "Google Antigravity / Gemini"),
        ("RENDER_API_KEY", "Render Cloud API"),
    ]

    for key, desc in keys_to_check:
        val = get_env(key)
        if val:
            masked = val[:4] + "..." + val[-4:] if len(val) > 10 else "***"
            print(f"  ✅ {desc:<30} ({key}): {Colors.GREEN}{masked}{Colors.RESET}")
        else:
            print(f"  ⚠️  {desc:<30} ({key}): {Colors.YELLOW}Não configurado{Colors.RESET}")

    print(f"\n{Colors.DIM}Para configurar ou auto-detectar o projeto, execute: amb setup (ou python amb_v2/config/setup_project.py){Colors.RESET}")


if __name__ == "__main__":
    main()
