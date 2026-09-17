from typing import Optional
from config import require_env, log, Colors, ApiExecutionError
from integrations.common.base_google_client import BaseGoogleClient

class GeminiBackend:
    """Backend encapsulation for direct REST Google Gemini API invocation."""

    def __init__(self, api_key: Optional[str], google_client: BaseGoogleClient):
        self.api_key = api_key
        self.google_client = google_client

    def _generate_via_gemini_api(
        self,
        prompt: str,
        model: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 8192
    ) -> str:
        """Executa chamada direta à REST API do Google Gemini com retry e fallback inteligente."""
        if not self.api_key:
            require_env("GEMINI_API_KEY")

        # Modelos modernos de última geração para failover de quota
        models_to_try = [model]
        for fallback_m in ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.1-pro-preview"]:
            if fallback_m not in models_to_try:
                models_to_try.append(fallback_m)

        last_err = None
        for current_m in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_m}:generateContent"
            payload = {
                "contents": [
                    {
                        "parts": [{"text": prompt}]
                    }
                ],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_output_tokens
                }
            }

            if system_instruction:
                payload["systemInstruction"] = {
                    "parts": [{"text": system_instruction}]
                }

            try:
                resp_data = self.google_client.execute_request(
                    method="POST",
                    path_or_url=url,
                    params={"key": self.api_key},
                    data=payload,
                    timeout=35,
                )
                candidates = resp_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
                raise ApiExecutionError("Resposta vazia retornada pelo modelo Gemini.")
            except ApiExecutionError as e:
                last_err = e
                # Se for 429 ou 503, tenta o próximo modelo de fallback
                if "429" in str(e) or "503" in str(e) or "Rate Limit" in getattr(e, "hint", ""):
                    log("ANTIGRAVITY", f"Limite ou instabilidade no modelo ({current_m}). Tentando fallback...", Colors.YELLOW)
                    continue
                raise e
            except Exception as e:
                last_err = ApiExecutionError(f"Falha de conexão com a API do Gemini ({current_m}): {e}")
                continue

        raise last_err or ApiExecutionError("Falha na chamada REST dos modelos Gemini.")
