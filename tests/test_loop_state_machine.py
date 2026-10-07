import pytest
import json
import os
from pathlib import Path
from amb_cli.agents.loop_core.loop_state_machine import LoopStateMachine, LoopState

@pytest.fixture
def temp_amb_dir(tmp_path):
    amb_dir = tmp_path / ".amb"
    amb_dir.mkdir()
    return amb_dir

def test_initial_state(temp_amb_dir):
    machine = LoopStateMachine(amb_dir=temp_amb_dir)
    assert machine.state == LoopState.IDLE
    assert machine.current_cycle == 0
    assert machine.total_cycles == 0

def test_transition_and_persistence(temp_amb_dir):
    machine = LoopStateMachine(amb_dir=temp_amb_dir)
    machine.transition_to(
        LoopState.DISPATCHING_JULES,
        current_cycle=1,
        total_cycles=5,
        active_item="agenda.md",
        session_id="sess_123"
    )

    # Verifica o estado em memória
    assert machine.state == LoopState.DISPATCHING_JULES
    assert machine.current_cycle == 1
    assert machine.total_cycles == 5
    assert machine.active_item == "agenda.md"
    assert machine.session_id == "sess_123"

    # Verifica a persistência
    state_file = temp_amb_dir / "loop_state.json"
    assert state_file.exists()

    with open(state_file, "r") as f:
        data = json.load(f)

    assert data["state"] == LoopState.DISPATCHING_JULES.value
    assert data["current_cycle"] == 1
    assert data["active_item"] == "agenda.md"

def test_load_existing_state(temp_amb_dir):
    # Cria estado inicial falso
    state_file = temp_amb_dir / "loop_state.json"
    fake_state = {
        "state": LoopState.RUNNING_LOCAL_QA.value,
        "current_cycle": 3,
        "total_cycles": 3,
        "active_item": "login",
        "session_id": "sess_456"
    }
    with open(state_file, "w") as f:
        json.dump(fake_state, f)

    machine = LoopStateMachine(amb_dir=temp_amb_dir)
    assert machine.state == LoopState.RUNNING_LOCAL_QA
    assert machine.current_cycle == 3
    assert machine.active_item == "login"
    assert machine.session_id == "sess_456"

def test_corrupted_json_recovery(temp_amb_dir):
    state_file = temp_amb_dir / "loop_state.json"
    with open(state_file, "w") as f:
        f.write("{ invalid json")

    machine = LoopStateMachine(amb_dir=temp_amb_dir)
    # Deve recuperar graciosamente para o IDLE
    assert machine.state == LoopState.IDLE

def test_pause_and_resume(temp_amb_dir):
    machine = LoopStateMachine(amb_dir=temp_amb_dir)
    machine.transition_to(LoopState.MONITORING_SESSION, current_cycle=2)

    # Pausar
    machine.pause()
    assert machine.state == LoopState.PAUSED

    # Transições durante PAUSED devem ser ignoradas
    machine.transition_to(LoopState.MERGING_PR)
    assert machine.state == LoopState.PAUSED

    # Retomar
    machine.resume()
    assert machine.state == LoopState.MONITORING_SESSION

def test_invalid_state_string_in_json(temp_amb_dir):
    state_file = temp_amb_dir / "loop_state.json"
    fake_state = {
        "state": "INVALID_STATE_BLABLA",
        "current_cycle": 1
    }
    with open(state_file, "w") as f:
        json.dump(fake_state, f)

    machine = LoopStateMachine(amb_dir=temp_amb_dir)
    assert machine.state == LoopState.IDLE
