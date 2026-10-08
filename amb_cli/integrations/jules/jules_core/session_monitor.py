import time
from typing import Dict, Any, Tuple, Callable, Optional

from integrations.jules.jules_client import JulesClient
from integrations.jules.jules_core.session_state import SessionState
from core import log_error


class SessionMonitor:
    """Monitor de sessões com polling unificado e callbacks baseados em estado."""

    def __init__(self, client: JulesClient, session_id: str):
        self.client = client
        self.session_id = session_id

    def poll_until_terminal(
        self,
        interval_seconds: int = 8,
        max_wait_seconds: int = 1800,
        on_state_change: Optional[Callable[[SessionState, Dict[str, Any]], None]] = None,
        on_tick: Optional[Callable[[SessionState, Dict[str, Any]], None]] = None,
        stop_condition: Optional[Callable[[SessionState, Dict[str, Any]], bool]] = None,
    ) -> Tuple[SessionState, Dict[str, Any]]:
        """
        Vigia a sessão até que ela atinja um estado terminal ou o tempo limite expire.

        Retorna:
            Tuple[SessionState, Dict[str, Any]]: Estado final da sessão e dados completos.
        """
        start_time = time.time()
        last_state = None
        session_data = {}

        while True:
            try:
                # 1. Checar Timeout
                if time.time() - start_time > max_wait_seconds:
                    log_error("SESSION-MONITOR", f"Timeout atingido ({max_wait_seconds}s) para sessão {self.session_id}")
                    # Retorna estado final conhecido e dados
                    current_state = SessionState.from_api_string(session_data.get("state", "")) if session_data else SessionState.IDLE
                    return current_state, session_data

                # 2. Obter Dados
                clean_id = self.session_id.split("/")[-1]
                session_data = self.client.get_session(clean_id)
                raw_state = session_data.get("state", "")
                current_state = SessionState.from_api_string(raw_state)

                # 3. Disparar Callback em Mudanças
                if current_state != last_state:
                    if on_state_change:
                        try:
                            on_state_change(current_state, session_data)
                        except Exception as cb_err:
                            log_error("SESSION-MONITOR", f"Erro no callback on_state_change: {cb_err}")
                    last_state = current_state

                # 4. Disparar Callback a cada Tick
                if on_tick:
                    try:
                        on_tick(current_state, session_data)
                    except Exception as tick_err:
                        log_error("SESSION-MONITOR", f"Erro no callback on_tick: {tick_err}")

                # 5. Checar Condições de Parada
                if stop_condition and stop_condition(current_state, session_data):
                    return current_state, session_data

                # 6. Checar Terminação
                if current_state.is_terminal():
                    runtime = time.time() - start_time
                    metrics = SessionState.extract_metrics(session_data, duration_seconds=runtime)
                    try:
                        from core.local_telemetry import LocalTelemetry
                        LocalTelemetry.record_session_metrics(
                            session_id=self.session_id,
                            runtime=metrics.get("runtime", runtime),
                            files_changed=metrics.get("files_changed", 0),
                            lines_added=metrics.get("lines_added", 0),
                            lines_removed=metrics.get("lines_removed", 0),
                            pr_url=metrics.get("pr_url"),
                        )
                    except Exception as tel_err:
                        log_error("SESSION-MONITOR", f"Falha ao registrar telemetria da sessão: {tel_err}")
                    return current_state, session_data

            except Exception as e:
                # Tratar exceções transitórias de rede / API
                log_error("SESSION-MONITOR", f"Erro transitório no polling da sessão {self.session_id}: {e}")

            # 7. Aguardar e Tentar Novamente
            time.sleep(interval_seconds)
