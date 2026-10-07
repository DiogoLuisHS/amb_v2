import os
import json
import enum
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# AMB standard paths logic
def _get_amb_dir() -> Path:
    # A simple way to get .amb relative to the repo root.
    # In full codebase, we'd use core workspace utils, but this handles it safely.
    repo_root = Path.cwd()
    # Find .amb directory starting from current working directory
    amb_dir = repo_root / ".amb"
    amb_dir.mkdir(parents=True, exist_ok=True)
    return amb_dir


class LoopState(str, enum.Enum):
    IDLE = "IDLE"
    SELECTING_PERSONA = "SELECTING_PERSONA"
    DISPATCHING_JULES = "DISPATCHING_JULES"
    MONITORING_SESSION = "MONITORING_SESSION"
    RUNNING_LOCAL_QA = "RUNNING_LOCAL_QA"
    MERGING_PR = "MERGING_PR"
    CYCLE_COMPLETED = "CYCLE_COMPLETED"
    PAUSED = "PAUSED"
    FAILED = "FAILED"


class LoopStateMachine:
    """Máquina de estados finita para gerenciar persistência do autonomous loop."""

    def __init__(self, amb_dir: Optional[Path] = None):
        if amb_dir is None:
            amb_dir = _get_amb_dir()
        self.state_file = amb_dir / "loop_state.json"

        self.state: LoopState = LoopState.IDLE
        self.current_cycle: int = 0
        self.total_cycles: int = 0
        self.active_item: Optional[str] = None
        self.session_id: Optional[str] = None
        self.updated_at: str = datetime.now().isoformat()

        # We need a field to remember previous state if paused
        self._previous_state: LoopState = LoopState.IDLE

        self.load_state()

    def load_state(self) -> None:
        """Carrega o estado a partir do arquivo JSON (com tolerância a falhas)."""
        if not self.state_file.exists():
            self.reset()
            return

        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            state_str = data.get("state", LoopState.IDLE.value)
            try:
                self.state = LoopState(state_str)
            except ValueError:
                self.state = LoopState.IDLE

            self.current_cycle = data.get("current_cycle", 0)
            self.total_cycles = data.get("total_cycles", 0)
            self.active_item = data.get("active_item", None)
            self.session_id = data.get("session_id", None)
            self.updated_at = data.get("updated_at", datetime.now().isoformat())

            # Internal
            prev_str = data.get("_previous_state", LoopState.IDLE.value)
            try:
                self._previous_state = LoopState(prev_str)
            except ValueError:
                self._previous_state = LoopState.IDLE

        except (json.JSONDecodeError, IOError):
            # Recuperação graciosa se o arquivo estiver corrompido ou inacessível
            self.reset()

    def save_state(self) -> None:
        """Salva o estado no disco de forma atômica."""
        self.updated_at = datetime.now().isoformat()
        data = {
            "state": self.state.value,
            "current_cycle": self.current_cycle,
            "total_cycles": self.total_cycles,
            "active_item": self.active_item,
            "session_id": self.session_id,
            "updated_at": self.updated_at,
            "_previous_state": self._previous_state.value
        }

        # Atomic write
        tmp_file = self.state_file.with_suffix(".json.tmp")
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_file, self.state_file)
        except IOError:
            # Tolerância a falhas na gravação (ex: disco cheio, permissão)
            if tmp_file.exists():
                try:
                    tmp_file.unlink()
                except OSError:
                    pass

    def transition_to(self, new_state: LoopState, **kwargs: Any) -> None:
        """Transita para um novo estado com parâmetros opcionais."""
        # Se estamos pausados, não podemos transitar para outros estados (exceto recuperar)
        # a menos que seja para um reset ou fail
        if self.state == LoopState.PAUSED and new_state not in [LoopState.IDLE, LoopState.FAILED]:
            # A transição é ignorada se pausado, aguardar resume.
            # (Pode-se também lançar exceção, mas tolerância é melhor).
            return

        self.state = new_state

        if "current_cycle" in kwargs:
            self.current_cycle = kwargs["current_cycle"]
        if "total_cycles" in kwargs:
            self.total_cycles = kwargs["total_cycles"]
        if "active_item" in kwargs:
            self.active_item = kwargs["active_item"]
        if "session_id" in kwargs:
            self.session_id = kwargs["session_id"]

        self.save_state()

    def pause(self) -> None:
        """Pausa a execução, salvando o estado anterior."""
        if self.state != LoopState.PAUSED:
            self._previous_state = self.state
            self.state = LoopState.PAUSED
            self.save_state()

    def resume(self) -> None:
        """Retoma a execução a partir do estado anterior."""
        if self.state == LoopState.PAUSED:
            self.state = self._previous_state
            self.save_state()

    def reset(self) -> None:
        """Reseta a máquina de estados para o estado inicial."""
        self.state = LoopState.IDLE
        self.current_cycle = 0
        self.total_cycles = 0
        self.active_item = None
        self.session_id = None
        self._previous_state = LoopState.IDLE
        self.save_state()

    def get_current_state(self) -> Dict[str, Any]:
        """Retorna um dicionário com o estado atual (para exibir no CLI)."""
        return {
            "state": self.state.value,
            "current_cycle": self.current_cycle,
            "total_cycles": self.total_cycles,
            "active_item": self.active_item,
            "session_id": self.session_id,
            "updated_at": self.updated_at
        }
