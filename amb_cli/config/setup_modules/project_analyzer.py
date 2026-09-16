import os
import re
import json
from typing import Dict, Any, Optional


class ProjectAnalyzer:
    """Extrai informações estruturais, linguagens, ferramentas e comandos de QA do repositório."""

    @staticmethod
    def detect_git_repo(root: str) -> Optional[str]:
        """Tenta identificar o owner/repo do git remote origin via GitService."""
        try:
            from integrations.git.git_service import GitService
            return GitService(repo_root=root).detect_github_repo(cwd=root)
        except Exception:
            return None

    @staticmethod
    def detect_stack(root: str) -> Dict[str, Any]:
        """Identifica linguagem principal, frameworks, gerenciador de pacotes e regras do projeto."""
        stack = {
            "type": "generic",
            "primary_language": "unknown",
            "frameworks": [],
            "package_manager": "npm",
            "is_monorepo": False,
            "rules_dir": None,
        }

        # Verifica marcadores de monorepo na raiz
        if (
            os.path.exists(os.path.join(root, "pnpm-workspace.yaml"))
            or os.path.exists(os.path.join(root, "turbo.json"))
            or os.path.exists(os.path.join(root, "lerna.json"))
        ):
            stack["is_monorepo"] = True

        search_dirs = [root]
        for sub in ["apps", "app", "packages", "src", "frontend", "backend", "web", "api"]:
            p = os.path.join(root, sub)
            if os.path.exists(p) and os.path.isdir(p):
                search_dirs.append(p)
                if sub in ["apps", "packages"]:
                    stack["is_monorepo"] = True
                try:
                    for child in os.listdir(p):
                        cp = os.path.join(p, child)
                        if os.path.isdir(cp):
                            search_dirs.append(cp)
                except Exception:
                    pass

        has_node = False
        has_python = False
        has_go = False
        has_rust = False

        # 1. Package Manager & Node/TS Stack
        for sdir in search_dirs:
            if os.path.exists(os.path.join(sdir, "bun.lock")) or os.path.exists(os.path.join(sdir, "bun.lockb")):
                stack["package_manager"] = "bun"
                has_node = True
            elif os.path.exists(os.path.join(sdir, "pnpm-lock.yaml")):
                stack["package_manager"] = "pnpm"
                has_node = True
            elif os.path.exists(os.path.join(sdir, "yarn.lock")):
                stack["package_manager"] = "yarn"
                has_node = True

            pkg_path = os.path.join(sdir, "package.json")
            if os.path.exists(pkg_path):
                has_node = True
                try:
                    with open(pkg_path, "r", encoding="utf-8") as f:
                        pkg = json.load(f)
                        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                        if "react" in deps or "next" in deps:
                            fw = "React" if "react" in deps else "Next.js"
                            if fw not in stack["frameworks"]:
                                stack["frameworks"].append(fw)
                        if "vue" in deps or "nuxt" in deps:
                            fw = "Vue" if "vue" in deps else "Nuxt.js"
                            if fw not in stack["frameworks"]:
                                stack["frameworks"].append(fw)
                        if "hono" in deps and "Hono" not in stack["frameworks"]:
                            stack["frameworks"].append("Hono")
                        if "express" in deps and "Express" not in stack["frameworks"]:
                            stack["frameworks"].append("Express")
                        if "fastify" in deps and "Fastify" not in stack["frameworks"]:
                            stack["frameworks"].append("Fastify")
                        if ("tailwindcss" in deps or "@tailwindcss/vite" in deps) and "TailwindCSS" not in stack["frameworks"]:
                            stack["frameworks"].append("TailwindCSS")
                        if "drizzle-orm" in deps and "Drizzle ORM" not in stack["frameworks"]:
                            stack["frameworks"].append("Drizzle ORM")
                        if ("prisma" in deps or "@prisma/client" in deps) and "Prisma" not in stack["frameworks"]:
                            stack["frameworks"].append("Prisma")
                        if "@google/stitch-sdk" in deps and "Stitch SDK" not in stack["frameworks"]:
                            stack["frameworks"].append("Stitch SDK")
                except Exception:
                    pass

            # 2. Python Stack
            if os.path.exists(os.path.join(sdir, "poetry.lock")):
                stack["package_manager"] = "poetry"
                has_python = True
            elif os.path.exists(os.path.join(sdir, "uv.lock")):
                stack["package_manager"] = "uv"
                has_python = True

            for py_file in ["pyproject.toml", "requirements.txt", "Pipfile"]:
                pypath = os.path.join(sdir, py_file)
                if os.path.exists(pypath):
                    has_python = True
                    try:
                        with open(pypath, "r", encoding="utf-8", errors="replace") as f:
                            c = f.read().lower()
                            if "fastapi" in c and "FastAPI" not in stack["frameworks"]:
                                stack["frameworks"].append("FastAPI")
                            if "django" in c and "Django" not in stack["frameworks"]:
                                stack["frameworks"].append("Django")
                            if "flask" in c and "Flask" not in stack["frameworks"]:
                                stack["frameworks"].append("Flask")
                            if "sqlalchemy" in c and "SQLAlchemy" not in stack["frameworks"]:
                                stack["frameworks"].append("SQLAlchemy")
                            if "pydantic" in c and "Pydantic" not in stack["frameworks"]:
                                stack["frameworks"].append("Pydantic")
                            if "pytest" in c and "Pytest" not in stack["frameworks"]:
                                stack["frameworks"].append("Pytest")
                    except Exception:
                        pass

            # 3. Go Stack
            if os.path.exists(os.path.join(sdir, "go.mod")):
                has_go = True
                if "Go" not in stack["frameworks"]:
                    stack["frameworks"].append("Go")

            # 4. Rust Stack
            if os.path.exists(os.path.join(sdir, "Cargo.toml")):
                has_rust = True
                if "Rust" not in stack["frameworks"]:
                    stack["frameworks"].append("Rust")

        # Classificação do tipo e linguagem principal
        if has_node and has_python:
            stack["type"] = "hybrid (Node/Python)"
            stack["primary_language"] = "typescript/python"
            stack["package_manager"] = f"{stack['package_manager']} / pip"
        elif has_node:
            stack["type"] = "node/typescript"
            stack["primary_language"] = "typescript"
        elif has_python:
            stack["type"] = "python"
            stack["primary_language"] = "python"
            if stack["package_manager"] not in ["poetry", "uv"]:
                stack["package_manager"] = "pip"
        elif has_go:
            stack["type"] = "go"
            stack["primary_language"] = "go"
            stack["package_manager"] = "go modules"
        elif has_rust:
            stack["type"] = "rust"
            stack["primary_language"] = "rust"
            stack["package_manager"] = "cargo"

        # 5. Rules Directory
        for candidate in [".antigravity/rules", ".gemini/rules", "rules"]:
            if os.path.exists(os.path.join(root, candidate)):
                stack["rules_dir"] = candidate
                break

        return stack

    @staticmethod
    def infer_qa_commands(stack: Dict[str, Any], root: str) -> Dict[str, str]:
        """Infere comandos de QA precisos (typecheck, lint, test, build) baseados na stack e manifestos."""
        qa: Dict[str, str] = {}
        stype = stack.get("type", "").lower()
        pm = stack.get("package_manager", "npm").split()[0]
        run_prefix = f"{pm} run" if pm in ["npm", "pnpm", "yarn"] else pm

        # 1. Stack Node/TypeScript
        if "node" in stype:
            root_pkg_path = os.path.join(root, "package.json")
            scripts = {}
            if os.path.exists(root_pkg_path):
                try:
                    with open(root_pkg_path, "r", encoding="utf-8") as f:
                        scripts = json.load(f).get("scripts", {})
                except Exception:
                    scripts = {}

            if "typecheck" in scripts:
                qa["typecheck"] = f"{run_prefix} typecheck"
            elif os.path.exists(os.path.join(root, "tsconfig.json")):
                qa["typecheck"] = "npx tsc --noEmit"

            if "lint" in scripts:
                qa["lint"] = f"{run_prefix} lint"

            if "test" in scripts:
                qa["test"] = f"{pm} test" if pm != "bun" else "bun test"

            if "build" in scripts:
                qa["build"] = f"{run_prefix} build"

        # 2. Stack Python
        elif "python" in stype:
            pm_tool = stack.get("package_manager", "pip")
            prefix = ""
            if pm_tool == "poetry":
                prefix = "poetry run "
            elif pm_tool == "uv":
                prefix = "uv run "

            has_pytest = "Pytest" in stack.get("frameworks", []) or os.path.exists(os.path.join(root, "tests"))
            if has_pytest:
                qa["test"] = f"{prefix}pytest"

            if os.path.exists(os.path.join(root, "mypy.ini")) or os.path.exists(os.path.join(root, ".mypy_cache")):
                qa["typecheck"] = f"{prefix}mypy ."
            elif os.path.exists(os.path.join(root, "cli.py")):
                qa["typecheck"] = "python -m py_compile cli.py"

            if os.path.exists(os.path.join(root, "ruff.toml")) or os.path.exists(os.path.join(root, ".ruff.toml")):
                qa["lint"] = f"{prefix}ruff check"
            elif os.path.exists(os.path.join(root, ".flake8")):
                qa["lint"] = f"{prefix}flake8"

            # Default syntax check se nada encontrado
            if not qa:
                qa["build"] = "python -m py_compile cli.py" if os.path.exists(os.path.join(root, "cli.py")) else "python -V"

        # 3. Stack Go
        elif "go" in stype:
            qa["typecheck"] = "go vet ./..."
            qa["build"] = "go build ./..."
            qa["test"] = "go test ./..."

        # 4. Stack Rust
        elif "rust" in stype:
            qa["typecheck"] = "cargo check"
            qa["build"] = "cargo build"
            qa["test"] = "cargo test"

        return qa
