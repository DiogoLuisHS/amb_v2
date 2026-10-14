from typing import Optional
from core import require_env, log, Colors, ApiExecutionError
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
        max_output_tokens: int = 8192,
        image_path: Optional[str] = None,
    ) -> str:
        """Executa chamada direta à REST API do Google Gemini com retry e fallback inteligente."""
        if not self.api_key:
            require_env("GEMINI_API_KEY")

        # Modelos modernos de última geração para failover de quota
        models_to_try = [model]
        for fallback_m in ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.1-pro-preview"]:
            if fallback_m not in models_to_try:
                models_to_try.append(fallback_m)

        # Monta parts com texto e imagem multimodal se fornecida
        parts = [{"text": prompt}]
        if image_path:
            import base64
            import os
            if os.path.exists(image_path):
                ext = os.path.splitext(image_path)[1].lower()
                mime = "image/png"
                if ext in [".jpg", ".jpeg"]:
                    mime = "image/jpeg"
                elif ext == ".webp":
                    mime = "image/webp"
                with open(image_path, "rb") as f_img:
                    b64_data = base64.b64encode(f_img.read()).decode("utf-8")
                parts.append({
                    "inlineData": {
                        "mimeType": mime,
                        "data": b64_data
                    }
                })

        last_err = None
        for current_m in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_m}:generateContent"
            payload = {
                "contents": [
                    {
                        "parts": parts
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

    def _generate_stream_via_gemini_api(
        self,
        prompt: str,
        model: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 8192,
        image_path: Optional[str] = None,
    ):
        """Executa chamada à REST API do Google Gemini (SSE) retornando os chunks de texto via yield."""
        import json

        if not self.api_key:
            require_env("GEMINI_API_KEY")

        models_to_try = [model]
        for fallback_m in ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.1-pro-preview"]:
            if fallback_m not in models_to_try:
                models_to_try.append(fallback_m)

        parts = [{"text": prompt}]
        if image_path:
            import base64
            import os
            if os.path.exists(image_path):
                ext = os.path.splitext(image_path)[1].lower()
                mime = "image/png"
                if ext in [".jpg", ".jpeg"]:
                    mime = "image/jpeg"
                elif ext == ".webp":
                    mime = "image/webp"
                with open(image_path, "rb") as f_img:
                    b64_data = base64.b64encode(f_img.read()).decode("utf-8")
                parts.append({
                    "inlineData": {
                        "mimeType": mime,
                        "data": b64_data
                    }
                })

        last_err = None
        for current_m in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_m}:streamGenerateContent?alt=sse"
            payload = {
                "contents": [
                    {
                        "parts": parts
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
                # Retorna o generator
                stream_generator = self.google_client.execute_request(
                    method="POST",
                    path_or_url=url,
                    params={"key": self.api_key},
                    data=payload,
                    timeout=35,
                    stream=True,
                )

                def _chunk_generator():
                    for line in stream_generator:
                        line = line.strip()
                        if not line or not line.startswith("data: "):
                            continue

                        try:
                            data_json = json.loads(line[6:])
                            candidates = data_json.get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                if parts:
                                    chunk_text = parts[0].get("text", "")
                                    if chunk_text:
                                        yield chunk_text
                        except json.JSONDecodeError:
                            pass

                # Para validar falha na request, podemos apenas retornar o generator,
                # e os erros vão estourar ao iterar, mas para permitir fallback no `generate_text_stream`,
                # _chunk_generator vai soltar ApiExecutionError na iteracao se falhar.
                # Como a conexao e iterada em execute_stream_request,
                # e urllib pode lançar exceptions na iteração.

                return _chunk_generator()

            except ApiExecutionError as e:
                last_err = e
                if "429" in str(e) or "503" in str(e) or "Rate Limit" in getattr(e, "hint", ""):
                    log("ANTIGRAVITY", f"Limite ou instabilidade no modelo ({current_m}). Tentando fallback...", Colors.YELLOW)
                    continue
                raise e
            except Exception as e:
                last_err = ApiExecutionError(f"Falha de conexão com a API do Gemini ({current_m}): {e}")
                continue

        raise last_err or ApiExecutionError("Falha na chamada REST dos modelos Gemini (SSE).")
