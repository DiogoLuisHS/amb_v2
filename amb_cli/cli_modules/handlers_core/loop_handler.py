import sys
from typing import Any
from core import Colors
from agents.loop_core.loop_state_machine import LoopStateMachine, LoopState

def handle_cmd_loop(args: Any) -> None:
    """Roteador de comandos da CLI para a máquina de estados do loop (amb loop)."""
    sub_cmd = getattr(args, "loop_cmd", None)

    if not sub_cmd:
        print(f"{Colors.RED}Comando de loop ausente. Use: amb loop [status|pause|resume]{Colors.RESET}")
        sys.exit(1)

    machine = LoopStateMachine()

    if sub_cmd == "status":
        state_dict = machine.get_current_state()
        state_val = state_dict.get("state")

        # Colorize the state based on what it is
        if state_val == LoopState.PAUSED.value:
            color = Colors.YELLOW
        elif state_val == LoopState.FAILED.value:
            color = Colors.RED
        elif state_val == LoopState.CYCLE_COMPLETED.value:
            color = Colors.GREEN
        elif state_val == LoopState.IDLE.value:
            color = Colors.DIM
        else:
            color = Colors.CYAN

        print(f"\n{Colors.BOLD}{Colors.BLUE}=== AMB Loop Status ==={Colors.RESET}")
        print(f"Estado Atual: {color}{state_val}{Colors.RESET}")
        print(f"Ciclo Atual:  {state_dict.get('current_cycle', 0)} / {state_dict.get('total_cycles', 0)}")
        print(f"Item Ativo:   {state_dict.get('active_item', 'Nenhum')}")
        print(f"Sessão Jules: {state_dict.get('session_id', 'Nenhuma')}")
        print(f"Atualizado:   {state_dict.get('updated_at', 'Desconhecido')}\n")

    elif sub_cmd == "pause":
        if machine.state == LoopState.PAUSED:
            print(f"{Colors.YELLOW}O loop já está pausado.{Colors.RESET}")
        else:
            machine.pause()
            print(f"{Colors.GREEN}Loop pausado com sucesso. Estado anterior salvo.{Colors.RESET}")

    elif sub_cmd == "resume":
        if machine.state != LoopState.PAUSED:
            print(f"{Colors.YELLOW}O loop não está pausado (Estado: {machine.state.value}).{Colors.RESET}")
        else:
            machine.resume()
            print(f"{Colors.GREEN}Loop retomado. Estado alterado para: {machine.state.value}{Colors.RESET}")

    else:
        print(f"{Colors.RED}Comando desconhecido: {sub_cmd}{Colors.RESET}")
        sys.exit(1)
