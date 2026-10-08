import os
import re

def synthesize_session_title(prompt_or_path: str, max_chars: int = 60) -> str:
    """
    Sintetiza um título curto e amigável para a sessão do Jules a partir do prompt
    ou do conteúdo de um arquivo markdown.

    Args:
        prompt_or_path: O texto do prompt ou o caminho para um arquivo.
        max_chars: Número máximo de caracteres do título retornado.

    Returns:
        Um título em string limpo e truncado se necessário.
    """
    if not prompt_or_path or not str(prompt_or_path).strip():
        return "Sessão AMB_V2"

    prompt_str = str(prompt_or_path).strip()

    # Verifica se é um arquivo existente no sistema de arquivos
    is_file = False
    try:
        # Usar um limite de tamanho de string para isfile para não quebrar com prompts enormes
        if len(prompt_str) < 2048 and os.path.isfile(prompt_str):
            is_file = True
    except Exception:
        pass

    if is_file:
        try:
            with open(prompt_str, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        cleaned = _clean_and_truncate(line, max_chars)
                        if cleaned != "Sessão AMB_V2":
                            return cleaned
        except Exception:
            pass

        # Fallback para o nome base do arquivo se a leitura falhar ou o arquivo estiver vazio
        base = os.path.splitext(os.path.basename(prompt_str))[0]
        return _clean_and_truncate(base.replace("_", " "), max_chars)

    # Se não for arquivo, tratar como texto direto
    return _clean_and_truncate(prompt_str, max_chars)


def _clean_and_truncate(text: str, max_chars: int) -> str:
    """Limpa marcações markdown da primeira linha de um texto e aplica truncamento."""
    if not text:
        return "Sessão AMB_V2"

    # Pega apenas a primeira linha
    text = text.splitlines()[0].strip()

    # Remove marcações markdown iniciais e espaços (#, *, >, -)
    text = re.sub(r'^[\#\*\>\-\s]+', '', text)

    # Remove espaços extras (múltiplos espaços)
    text = " ".join(text.split())

    if not text:
        return "Sessão AMB_V2"

    if len(text) > max_chars:
        # Adiciona '...' respeitando o max_chars total
        return text[:max_chars - 3] + "..."

    return text
