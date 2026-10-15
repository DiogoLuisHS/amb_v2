import os
import re
from typing import List, Dict, Any, Optional

from amb_cli.core import Colors, log, log_error
from amb_cli.workspace.project_context import find_repo_root, load_project_json

class PersonaEngine:
    """Engine unificada de personas com descoberta, interpolação e validação."""

    def __init__(self, repo_root: Optional[str] = None):
        self.repo_root = repo_root or find_repo_root()
        self.personas_dir = os.path.join(self.repo_root, ".amb", "personas")
        self.project_context = load_project_json(self.repo_root)

    def load_persona(self, name: str) -> Optional[str]:
        """
        Busca prioritariamente no diretório .amb/personas/ do projeto.
        Se não existir, recorre aos fallbacks.
        """
        if not name.endswith(".md"):
            name += ".md"

        filepath = os.path.join(self.personas_dir, name)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                return f.read()

        # Fallback para o diretório de agentes do próprio AMB
        amb_pkg_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".agents", "skills"))

        # Vamos assumir que as personas de fallback possam estar em .agents/skills ou .amb/prompts ou hardcoded
        # A issue pede: "recorrer aos fallbacks padrão de engenharia sem quebrar o fluxo".

        fallback_dir = os.path.join(amb_pkg_dir)
        if os.path.exists(fallback_dir):
            clean_name = name.replace(".md", "")
            for skill_dir in os.listdir(fallback_dir):
                target_skill = os.path.join(fallback_dir, skill_dir)
                if not os.path.isdir(target_skill):
                    continue
                if clean_name in skill_dir:
                    skill_file = os.path.join(target_skill, "SKILL.md")
                    if os.path.exists(skill_file):
                        with open(skill_file, "r", encoding="utf-8", errors="replace") as f:
                            return f.read()
                subskills_dir = os.path.join(target_skill, "subskills")
                if os.path.exists(subskills_dir) and os.path.isdir(subskills_dir):
                    for subfile in os.listdir(subskills_dir):
                        if clean_name in subfile.replace(".md", ""):
                            sub_path = os.path.join(subskills_dir, subfile)
                            with open(sub_path, "r", encoding="utf-8", errors="replace") as f:
                                return f.read()

        return None

    def render_persona_template(self, content: str, context_vars: Optional[Dict[str, Any]] = None) -> str:
        """Interpola valores a partir do contexto do projeto."""
        vars_to_interpolate = {
            "repo_name": os.path.basename(self.repo_root),
            "stack": self.project_context.get("stack", "unknown"),
            "qa_command": self.project_context.get("qa_command", "npm test")
        }

        if context_vars:
            vars_to_interpolate.update(context_vars)

        rendered_content = content
        for key, value in vars_to_interpolate.items():
            placeholder = "{" + key + "}"
            rendered_content = rendered_content.replace(placeholder, str(value))

        return rendered_content

    def validate_persona_file(self, filepath: str) -> List[str]:
        """
        Verifica se a persona possui:
        - Título/Missão (#)
        - Foco de Arquivos (## Arquivos)
        - Regras de Implementação (## Regras)
        Retorna lista de erros.
        """
        errors = []
        if not os.path.exists(filepath):
            errors.append(f"Arquivo não encontrado: {filepath}")
            return errors

        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        if not re.search(r"^#\s+.*", content, re.MULTILINE):
            errors.append("Falta a seção de Título/Missão (# Título)")

        if not re.search(r"^##\s+Arquivos.*", content, re.MULTILINE):
            errors.append("Falta a seção de Foco de Arquivos (## Arquivos)")

        if not re.search(r"^##\s+Regras.*", content, re.MULTILINE):
            errors.append("Falta a seção de Regras de Implementação (## Regras)")

        return errors


    def get_personas_directory(self, custom_dir: Optional[str] = None) -> str:
        """Resolve e retorna o diretório de personas com prioridade para o .amb do projeto."""
        root = self.repo_root
        if custom_dir:
            abs_custom = os.path.abspath(custom_dir)
            if not os.path.exists(abs_custom):
                os.makedirs(abs_custom, exist_ok=True)
            return abs_custom

        amb_personas = os.path.join(root, ".amb", "personas")
        if os.path.exists(amb_personas) and os.path.isdir(amb_personas):
            return os.path.abspath(amb_personas)

        jules_personas = os.path.join(root, ".jules", "personas")
        if os.path.exists(jules_personas) and os.path.isdir(jules_personas):
            return os.path.abspath(jules_personas)

        candidates = [
            os.path.join(root, ".amb"),
            os.path.join(root, ".jules"),
            os.path.join(root, "amb_cli", "agents", "personas"),
            os.path.join(os.path.dirname(__file__), "personas"),
            os.path.join(root, "amb_cli", "integrations", "antigravity", "personas"),
        ]

        for p in candidates:
            if os.path.exists(p) and os.path.isdir(p):
                # If it's one of the legacy non-personas dirs, check for md files
                if os.path.basename(p) in (".amb", ".jules"):
                    md_files = [f for f in os.listdir(p) if f.endswith(".md") and not f.startswith("_") and f.lower() != "readme.md"]
                    if md_files:
                        return os.path.abspath(p)
                else:
                    return os.path.abspath(p)

        default_dir = os.path.join(root, ".amb", "personas")
        os.makedirs(default_dir, exist_ok=True)
        return default_dir

    def discover_personas(self, custom_dir: Optional[str] = None) -> Dict[str, Dict[str, str]]:
        """Varre dinamicamente a pasta de personas e extrai metadados dos arquivos markdown."""
        personas_dir = self.get_personas_directory(custom_dir)
        personas = {}
        if not os.path.exists(personas_dir):
            return personas

        for fname in sorted(os.listdir(personas_dir)):
            if not fname.endswith(".md"):
                continue
            if fname.lower() in ["readme.md"] or fname.startswith("_"):
                continue

            key = os.path.splitext(fname)[0].lower()
            fpath = os.path.join(personas_dir, fname)

            title = key.capitalize()
            summary = "Agente de manutenção especializado."
            persona_content = ""

            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    persona_content = f.read().strip()

                m_title = re.search(r"^#\s+(.+)$", persona_content, re.MULTILINE)
                if m_title:
                    title = m_title.group(1).strip()

                lines = [l.strip() for l in persona_content.split("\n") if l.strip() and not l.startswith("#")]
                if lines:
                    summary = lines[0][:120] + ("..." if len(lines[0]) > 120 else "")
            except (OSError, IOError) as e:
                log_error("AGENT", f"Erro ao ler arquivo da persona '{fname}': {e}")
                continue

            personas[key] = {
                "key": key,
                "filename": fname,
                "path": fpath,
                "title": title,
                "summary": summary,
                "content": persona_content
            }

        return personas

    def list_personas(self, personas: Dict[str, Dict[str, str]], personas_dir: str) -> None:
        """Exibe no terminal a listagem dinâmica de todas as personas encontradas na pasta."""
        print("\n" + "=" * 75)
        print(f"{Colors.BOLD}{Colors.CYAN}🤖 PERSONAS DISPONÍVEIS NA PASTA ({len(personas)} encontradas){Colors.RESET}")
        print(f"📁 Diretório: {Colors.DIM}{personas_dir}{Colors.RESET}")
        print("=" * 75 + "\n")

        if not personas:
            print(f"{Colors.YELLOW}Nenhuma persona (.md) encontrada em: {personas_dir}{Colors.RESET}")
            print(f"Basta adicionar arquivos como '{personas_dir}/minha_persona.md' para ativá-las.\n")
            return

        for key, p in personas.items():
            print(f"  • {Colors.BOLD}{key:<12}{Colors.RESET} {Colors.GREEN}{p['title']}{Colors.RESET} (Arquivo: {p['filename']})")
            print(f"    Missão: {Colors.DIM}{p['summary']}{Colors.RESET}\n")

        print(f"{Colors.YELLOW}Como Executar:{Colors.RESET}")
        print(f"  • Despachar Jules (Padrão): amb agent --role <nome>  (ou python amb_cli/agents/local_agent_runner.py --role <nome>)")
        print(f"  • TODAS as Personas (Jules):  amb agent --all")
        print(f"  • Executar Local (agy CLI):   amb agent --role <nome> --agy (ou --local)")
        print(f"  • Pasta de Prompts (Lote):    amb agent -p .amb/prompts/ (executa todos os .md sequencialmente)\n")
