import subprocess
from pathlib import Path
from typing import Tuple, Optional, List, Dict, Any
from core.exceptions import AmbError

class SessionExtractor:
    """Extrai e aplica patches gerados em sessões do Jules."""

    @staticmethod
    def extract_commit_message(session_data: dict) -> Optional[str]:
        """Extrai a suggestedCommitMessage do gitPatch se presente nos outputs."""
        outputs = session_data.get("outputs", [])
        for out in outputs:
            msg = out.get("changeSet", {}).get("gitPatch", {}).get("suggestedCommitMessage")
            if msg:
                return str(msg).strip()
        return None

    @staticmethod
    def extract_bash_outputs(activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extrai todos os artefatos de bashOutput das atividades da sessão.
        Retorna lista de dicionários com 'command', 'output' e 'exitCode'.
        """
        bash_outputs = []
        if not activities:
            return bash_outputs

        for act in activities:
            if not isinstance(act, dict):
                continue

            artifacts = act.get("artifacts", [])
            if not isinstance(artifacts, list):
                continue

            for artifact in artifacts:
                if not isinstance(artifact, dict):
                    continue

                bash_out = artifact.get("bashOutput")
                if isinstance(bash_out, dict):
                    bash_outputs.append({
                        "command": bash_out.get("command", ""),
                        "output": bash_out.get("output", ""),
                        "exitCode": bash_out.get("exitCode", 0)
                    })

        return bash_outputs

    @staticmethod
    def extract_failure_reason(activities: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """Extrai o motivo de falha (reason) a partir dos eventos sessionFailed das atividades."""
        if not activities:
            return None

        # Percorrer em ordem reversa para encontrar a falha mais recente
        for act in reversed(activities):
            if not isinstance(act, dict):
                continue
            session_failed = act.get("sessionFailed", {})
            if not isinstance(session_failed, dict):
                continue
            reason = session_failed.get("reason")
            if reason and isinstance(reason, str):
                return reason.strip()

        return None

    @staticmethod
    def extract_review_rejection(activities: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """Extrai ressalvas ou reprovações emitidas pela etapa de Code Review do Jules."""
        if not activities:
            return None

        for act in reversed(activities):
            if not isinstance(act, dict):
                continue
            prog = act.get("progressUpdated", {})
            if isinstance(prog, dict):
                title = (prog.get("title") or "").strip()
                desc = (prog.get("description") or "").strip()
                if "#Mostly Correct#" in desc or "#Correct#" in desc:
                    continue
                if "#Partially Correct#" in desc or "#Incorrect#" in desc or any(m in desc for m in ["not ready for production", "critical issues", "major regressions"]):
                    lines = [ln.strip() for ln in desc.splitlines() if ln.strip()]
                    summary = lines[0] if lines else title
                    rating = None
                    for ln in lines:
                        if "#Partially Correct#" in ln or "#Incorrect#" in ln:
                            rating = ln
                        elif any(marker in ln for marker in ["not ready for production", "critical issues", "major regressions"]):
                            summary = ln
                    if rating:
                        return f"{title}: {rating} ({summary})"
                    return f"{title}: {summary}"
        return None

    @staticmethod
    def detect_activity_repetition(activities: List[Dict[str, Any]], threshold: int = 10) -> Optional[Tuple[int, List[str]]]:
        """Detecta repetições consecutivas de patches nos mesmos arquivos (potencial loop de agente)."""
        if not activities or len(activities) < threshold:
            return None

        recent = activities[-threshold:]
        file_sets: List[set] = []
        for act in recent:
            if not isinstance(act, dict):
                continue
            act_files = set()
            for art in act.get("artifacts", []):
                diff = art.get("changeSet", {}).get("gitPatch", {}).get("unidiffPatch", "")
                for line in diff.splitlines():
                    if line.startswith("+++ b/"):
                        act_files.add(line[6:].strip())
            if act_files:
                file_sets.append(act_files)

        if len(file_sets) >= threshold:
            common = file_sets[0]
            for s in file_sets[1:]:
                common = common.intersection(s)
            if common and all(len(s - common) == 0 for s in file_sets):
                return len(file_sets), sorted(list(common))

        return None

    @staticmethod
    def extract_patch(session_data: dict, activities: Optional[List[Dict[str, Any]]] = None) -> str:
        """Percorre os outputs da sessão ou atividades buscando o unidiffPatch."""
        outputs = session_data.get("outputs", [])
        if not outputs and not activities:
            raise AmbError(
                "A sessão não contém outputs.",
                "Certifique-se de que a sessão foi concluída e gerou alguma alteração no código."
            )

        for out in outputs:
            patch = out.get("changeSet", {}).get("gitPatch", {}).get("unidiffPatch")
            if patch:
                return patch

        if activities:
            for act in reversed(activities):
                if not isinstance(act, dict):
                    continue
                for art in act.get("artifacts", []):
                    if not isinstance(art, dict):
                        continue
                    patch = art.get("changeSet", {}).get("gitPatch", {}).get("unidiffPatch")
                    if patch:
                        return patch

        raise AmbError(
            "Nenhum patch de código (unidiffPatch) encontrado na sessão.",
            "Esta sessão pode não ter modificado nenhum arquivo ou não ter o formato esperado de output de código."
        )

    @staticmethod
    def save_patch(patch_content: str, dest_path: Path) -> Path:
        """Salva o conteúdo do patch em um arquivo."""
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(patch_content, encoding="utf-8", errors="replace")
        return dest_path

    @staticmethod
    def apply_patch(patch_content: str, repo_root: Path) -> Tuple[bool, str]:
        """Aplica o patch usando o comando git apply no repositório."""
        patch_file = repo_root / ".amb" / "tmp_extract.patch"
        try:
            patch_file.parent.mkdir(parents=True, exist_ok=True)
            patch_file.write_text(patch_content, encoding="utf-8", errors="replace")

            result = subprocess.run(
                ["git", "apply", str(patch_file.absolute())],
                cwd=str(repo_root),
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return True, "Patch aplicado com sucesso via 'git apply'."
            else:
                return False, f"Falha ao aplicar o patch. Erro do git:\n{result.stderr.strip()}"
        finally:
            if patch_file.exists():
                patch_file.unlink()
