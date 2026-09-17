import os
import re
from typing import Dict, Any, Optional

def parse_design_tokens_from_text(text: str) -> Dict[str, Any]:
    """Extrai tokens e diretrizes de design básicos de um texto Markdown (ex: design.md)."""
    tokens: Dict[str, Any] = {}
    if not text:
        return tokens

    # Cores hexadecimais explícitas
    hex_match = re.search(r'(?:primary|custom|brand|accent)[-_]?(?:color)?\s*[:=]\s*(#[0-9a-fA-F]{3,8})', text, re.IGNORECASE)
    if hex_match:
        tokens["customColor"] = hex_match.group(1)
    else:
        first_hex = re.search(r'#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', text)
        if first_hex:
            tokens["customColor"] = first_hex.group(0)

    # Modo de cor (LIGHT ou DARK)
    mode_match = re.search(r'(?:color[-_]?mode|mode|theme|tema|modo)\s*[:=]\s*(LIGHT|DARK|CLARO|ESCURO)', text, re.IGNORECASE)
    if mode_match:
        val = mode_match.group(1).upper()
        tokens["colorMode"] = "LIGHT" if val in ("LIGHT", "CLARO") else "DARK"

    # Fontes
    font_match = re.search(r'(?:font[-_]?(?:family|headline|body)?)\s*[:=]\s*["\']?([a-zA-Z0-9_\s]+)["\']?', text, re.IGNORECASE)
    if font_match:
        raw_font = font_match.group(1).strip().upper().replace(" ", "_")
        valid_fonts = [
            "BE_VIETNAM_PRO", "EPILOGUE", "INTER", "LEXEND", "MANROPE", "NEWSREADER",
            "NOTO_SERIF", "PLUS_JAKARTA_SANS", "PUBLIC_SANS", "SPACE_GROTESK", "SPLINE_SANS",
            "WORK_SANS", "DOMINE", "LIBRE_CASLON_TEXT", "EB_GARAMOND", "LITERATA",
            "SOURCE_SERIF_FOUR", "MONTSERRAT", "METROPOLIS", "SOURCE_SANS_THREE", "NUNITO_SANS",
            "ARIMO", "HANKEN_GROTESK", "RUBIK", "GEIST", "DM_SANS", "IBM_PLEX_SANS", "SORA"
        ]
        matched = next((f for f in valid_fonts if f in raw_font or raw_font in f), None)
        if matched:
            tokens["headlineFont"] = matched
            tokens["bodyFont"] = matched

    # Roundness
    round_match = re.search(r'(?:roundness|border[-_]?radius|raio|cantos)\s*[:=]\s*["\']?([a-zA-Z0-9_\s]+)["\']?', text, re.IGNORECASE)
    if round_match:
        raw_round = round_match.group(1).strip().upper()
        if "FOUR" in raw_round or "4" in raw_round:
            tokens["roundness"] = "ROUND_FOUR"
        elif "EIGHT" in raw_round or "8" in raw_round:
            tokens["roundness"] = "ROUND_EIGHT"
        elif "TWELVE" in raw_round or "12" in raw_round:
            tokens["roundness"] = "ROUND_TWELVE"
        elif "FULL" in raw_round:
            tokens["roundness"] = "ROUND_FULL"

    return tokens


def get_design_system_config(default_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Resolve as configurações de Design System estritamente a partir das orientações do projeto.
    """
    from amb_cli.config.config import find_repo_root, load_project_json, get_env
    config: Dict[str, Any] = {}
    root = find_repo_root()
    p_meta = load_project_json()

    # 1. Configurações do amb_project.json
    project_design = p_meta.get("design_system") or p_meta.get("design") or p_meta.get("theme") or {}
    if isinstance(project_design, dict):
        for k, v in project_design.items():
            if v is not None:
                config[k] = v

    # 2. Leitura e parse de design.md se existir
    candidates = [
        default_file,
        os.path.join(root, "design.md"),
        os.path.join(root, "docs", "design.md"),
        os.path.join(root, ".antigravity", "rules", "design.md"),
    ]
    resolved_file = next((p for p in candidates if p and os.path.exists(p)), None)
    if resolved_file:
        try:
            with open(resolved_file, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            parsed_tokens = parse_design_tokens_from_text(content)
            for k, v in parsed_tokens.items():
                if k not in config and v is not None:
                    config[k] = v
            config["designMd"] = content
            config["design_md_path"] = resolved_file
        except Exception:
            pass

    # 3. Variáveis de ambiente explícitas
    env_map = {
        "colorMode": get_env("STITCH_COLOR_MODE"),
        "customColor": get_env("STITCH_PRIMARY_COLOR") or get_env("STITCH_CUSTOM_COLOR"),
        "headlineFont": get_env("STITCH_HEADLINE_FONT") or get_env("STITCH_FONT"),
        "bodyFont": get_env("STITCH_BODY_FONT") or get_env("STITCH_FONT"),
        "roundness": get_env("STITCH_ROUNDNESS"),
        "displayName": get_env("STITCH_DESIGN_SYSTEM_NAME"),
    }
    for k, v in env_map.items():
        if v and k not in config:
            config[k] = v

    if "displayName" not in config and "display_name" not in config:
        project_name = p_meta.get("name")
        if project_name:
            config["displayName"] = f"{project_name} Design System"

    return config
