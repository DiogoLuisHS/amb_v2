import os
from typing import Any
from amb_cli.core import Colors, log
from amb_cli.agents.persona_engine import PersonaEngine

def cmd_persona_list(args: Any) -> None:
    """Lista as personas locais com badges de validação."""
    engine = PersonaEngine()

    if not os.path.exists(engine.personas_dir):
        print(f"{Colors.YELLOW}⚠️ Diretório de personas não encontrado em: {engine.personas_dir}{Colors.RESET}")
        return

    files = [f for f in os.listdir(engine.personas_dir) if f.endswith(".md")]
    if not files:
        print(f"{Colors.YELLOW}Nenhuma persona encontrada (.md).{Colors.RESET}")
        return

    print(f"{Colors.CYAN}📋 Personas locais em: {engine.personas_dir}{Colors.RESET}")
    print("-" * 50)

    for file in files:
        filepath = os.path.join(engine.personas_dir, file)
        errors = engine.validate_persona_file(filepath)
        name = file.replace(".md", "")

        if errors:
            print(f"- {Colors.BOLD}{name}{Colors.RESET}: ⚠️ Incompleta")
        else:
            print(f"- {Colors.BOLD}{name}{Colors.RESET}: ✅ Válida")
    print("-" * 50)


def cmd_persona_validate(args: Any) -> None:
    """Valida todas as personas na pasta .amb/personas/ do projeto."""
    engine = PersonaEngine()

    if not os.path.exists(engine.personas_dir):
        print(f"{Colors.YELLOW}⚠️ Diretório de personas não encontrado em: {engine.personas_dir}{Colors.RESET}")
        return

    print(f"{Colors.CYAN}🔍 Validando personas em: {engine.personas_dir}{Colors.RESET}")
    print("-" * 50)

    files = [f for f in os.listdir(engine.personas_dir) if f.endswith(".md")]

    if not files:
        print(f"{Colors.YELLOW}Nenhuma persona encontrada (.md).{Colors.RESET}")
        return

    all_valid = True
    for file in files:
        filepath = os.path.join(engine.personas_dir, file)
        errors = engine.validate_persona_file(filepath)

        if errors:
            all_valid = False
            print(f"❌ {Colors.RED}{file}{Colors.RESET}")
            for err in errors:
                print(f"   - {Colors.YELLOW}{err}{Colors.RESET}")
        else:
            print(f"✅ {Colors.GREEN}{file}{Colors.RESET} (Válido)")

    print("-" * 50)
    if all_valid:
        print(f"{Colors.GREEN}🚀 Todas as personas estão válidas e seguem o padrão.{Colors.RESET}")
    else:
        print(f"{Colors.RED}⚠️ Foram encontrados problemas em algumas personas.{Colors.RESET}")


def cmd_persona(args: Any) -> None:
    """Comando central para amb persona"""
    if not hasattr(args, "persona_cmd") or args.persona_cmd in [None, "list"]:
        cmd_persona_list(args)
    elif args.persona_cmd == "validate":
        cmd_persona_validate(args)
    else:
        print(f"{Colors.YELLOW}Comando persona desconhecido: {args.persona_cmd}{Colors.RESET}")
