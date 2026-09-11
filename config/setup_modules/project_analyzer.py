import os
import re
import json
import subprocess
from typing import Dict, Any, Optional


class ProjectAnalyzer:
    """Extrai informações estruturais e de ambiente do repositório local."""

    @staticmethod
    def detect_git_repo(root: str) -> Optional[str]:
        """Tenta identificar o owner/repo do git remote origin."""
        try:
            res = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if res.returncode == 0 and res.stdout.strip():
                url = res.stdout.strip()
                match = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", url)
                if match:
                    return f"{match.group(1)}/{match.group(2)}"
        except Exception:
            pass

        git_config = os.path.join(root, ".git", "config")
        if os.path.exists(git_config):
            try:
                with open(git_config, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                    match = re.search(
                        r"url\s*=\s*.*github\.com[:/]([^/]+)/([^/.]+)", content
                    )
                    if match:
                        return f"{match.group(1)}/{match.group(2)}"
            except Exception:
                pass
        return None

    @staticmethod
    def detect_stack(root: str) -> Dict[str, Any]:
        """Identifica linguagem, frameworks e ferramentas do projeto."""
        stack = {
            "type": "unknown",
            "frameworks": [],
            "package_manager": "npm",
            "has_render_yaml": os.path.exists(os.path.join(root, "render.yaml")),
            "rules_dir": None,
        }

        # Coleta manifestos da raiz e de subpastas conhecidas de monorepos
        search_dirs = [root]
        for sub in [
            "apps",
            "app",
            "packages",
            "src",
            "frontend",
            "backend",
            "web",
            "api",
        ]:
            p = os.path.join(root, sub)
            if os.path.exists(p) and os.path.isdir(p):
                search_dirs.append(p)
                try:
                    for child in os.listdir(p):
                        cp = os.path.join(p, child)
                        if os.path.isdir(cp):
                            search_dirs.append(cp)
                except Exception:
                    pass

        has_node = False
        has_python = False

        # 1. Package Manager & Node/TS Stack
        for sdir in search_dirs:
            if os.path.exists(os.path.join(sdir, "bun.lock")) or os.path.exists(
                os.path.join(sdir, "bun.lockb")
            ):
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
                        deps = {
                            **pkg.get("dependencies", {}),
                            **pkg.get("devDependencies", {}),
                        }
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
                        if (
                            "tailwindcss" in deps or "@tailwindcss/vite" in deps
                        ) and "TailwindCSS" not in stack["frameworks"]:
                            stack["frameworks"].append("TailwindCSS")
                        if (
                            "drizzle-orm" in deps
                            and "Drizzle ORM" not in stack["frameworks"]
                        ):
                            stack["frameworks"].append("Drizzle ORM")
                        if (
                            "prisma" in deps or "@prisma/client" in deps
                        ) and "Prisma" not in stack["frameworks"]:
                            stack["frameworks"].append("Prisma")
                        if (
                            "@google/stitch-sdk" in deps
                            and "Stitch SDK" not in stack["frameworks"]
                        ):
                            stack["frameworks"].append("Stitch SDK")
                except Exception:
                    pass

            # 2. Python Stack
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
                            if (
                                "sqlalchemy" in c
                                and "SQLAlchemy" not in stack["frameworks"]
                            ):
                                stack["frameworks"].append("SQLAlchemy")
                            if (
                                "pydantic" in c
                                and "Pydantic" not in stack["frameworks"]
                            ):
                                stack["frameworks"].append("Pydantic")
                    except Exception:
                        pass

        if has_node and has_python:
            stack["type"] = "hybrid (Node/Python)"
            stack["package_manager"] = f"{stack['package_manager']} / pip"
        elif has_node:
            stack["type"] = "node/typescript"
        elif has_python:
            stack["type"] = "python"
            stack["package_manager"] = "pip/poetry"

        # 3. Rules Directory
        for candidate in [".antigravity/rules", ".gemini/rules", "rules"]:
            if os.path.exists(os.path.join(root, candidate)):
                stack["rules_dir"] = candidate
                break

        return stack
