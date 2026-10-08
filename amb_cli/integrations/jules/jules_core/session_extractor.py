import subprocess
from pathlib import Path
from typing import Tuple
from core.exceptions import AmbError

class SessionExtractor:
    """Extrai e aplica patches gerados em sessões do Jules."""

    @staticmethod
    def extract_patch(session_data: dict) -> str:
        """Percorre os outputs da sessão buscando o unidiffPatch."""
        outputs = session_data.get("outputs", [])
        if not outputs:
            raise AmbError(
                "A sessão não contém outputs.",
                "Certifique-se de que a sessão foi concluída e gerou alguma alteração no código."
            )

        for out in outputs:
            patch = out.get("changeSet", {}).get("gitPatch", {}).get("unidiffPatch")
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
