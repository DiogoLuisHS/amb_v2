# -*- coding: utf-8 -*-
"""
🧠 AMB_V2 - Google Gemini Backend (SRP Core)
Localização: amb_cli/integrations/antigravity/antigravity_core/gemini_backend.py
Responsabilidade Única: Execução de chamadas REST (síncronas e SSE) à API do Gemini
com gestão determinística de timeouts, tipagem estrita e cadeia de fallbacks seguros.
"""

import base64
import json
import os
from typing import Any, Dict, Iterator, List, Optional

from core import ApiExecutionError, Colors, log, require_env
from integrations.common.base_google_client import BaseGoogleClient

# Modelos canônicos ativos oficiais do Google Gemini (3.8 e 2.5 GA)
# Modelos descontinuados como 3.6, 3.5 legados foram removidos da cadeia.
CANONICAL_FALLBACK_MODELS: List[str] = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
]


class GeminiBackend:
    """Backend encapsulation for direct REST Google Gemini API invocation."""

    def __init__(self, api_key: Optional[str], google_client: BaseGoogleClient):
        self.api_key = api_key
        self.google_client = google_client

    @staticmethod
    def _is_fallback_worthy_error(err: Exception) -> bool:
        """Determina se o erro autoriza o avanço imediato para o modelo de fallback."""
        err_str = str(err).lower()
        hint = getattr(err, "hint", None)
        hint_str = hint.lower() if isinstance(hint, str) else ""
        combined = f"{err_str} {hint_str}"
        if any(code in combined for code in ["404", "429", "503", "500", "502"]):
            return True
        keywords = [
            "not found", "not supported", "rate limit", "quota",
            "resource_exhausted", "overloaded", "unavailable", "deprecated",
            "model not active"
        ]
        return any(kw in combined for kw in keywords)

    def _build_model_chain(self, primary_model: str) -> List[str]:
        """Constrói a lista ordenada de modelos para tentativa com fallbacks seguros."""
        chain = [primary_model]
        for fallback_m in CANONICAL_FALLBACK_MODELS:
            if fallback_m not in chain:
                chain.append(fallback_m)
        return chain

    @staticmethod
    def _prepare_parts(prompt: str, image_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Prepara payload multipart com prompt textual e imagem codificada em base64 se fornecida."""
        parts: List[Dict[str, Any]] = [{"text": prompt}]
        if image_path and os.path.exists(image_path):
            ext = os.path.splitext(image_path)[1].lower()
            mime = "image/png"
            if ext in [".jpg", ".jpeg"]:
                mime = "image/jpeg"
            elif ext == ".webp":
                mime = "image/webp"
            with open(image_path, "rb") as f_img:
                b64_data = base64.b64encode(f_img.read()).decode("utf-8")
            parts.append({"inlineData": {"mimeType": mime, "data": b64_data}})
        return parts

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

        models_to_try = self._build_model_chain(model)
        parts = self._prepare_parts(prompt, image_path)
        last_err: Optional[Exception] = None

        for current_m in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_m}:generateContent"
            payload: Dict[str, Any] = {
                "contents": [{"parts": parts}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_output_tokens,
                },
            }
            if system_instruction:
                payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

            try:
                resp_data = self.google_client.execute_request(
                    method="POST", path_or_url=url, params={"key": self.api_key},
                    data=payload, timeout=35,
                )
                candidates = resp_data.get("candidates", [])
                if candidates:
                    cand_parts = candidates[0].get("content", {}).get("parts", [])
                    if cand_parts:
                        return cand_parts[0].get("text", "").strip()
                raise ApiExecutionError("Resposta vazia retornada pelo modelo Gemini.")
            except ApiExecutionError as e:
                last_err = e
                if self._is_fallback_worthy_error(e):
                    log("ANTIGRAVITY", f"Modelo {current_m} indisponível ou descontinuado. Tentando fallback...", Colors.YELLOW)
                    continue
                raise e
            except Exception as e:
                wrapped_err = ApiExecutionError(f"Falha de conexão com a API do Gemini ({current_m}): {e}")
                last_err = wrapped_err
                if self._is_fallback_worthy_error(wrapped_err):
                    log("ANTIGRAVITY", f"Falha de rede/modelo no Gemini ({current_m}). Tentando fallback...", Colors.YELLOW)
                    continue
                raise wrapped_err

        raise last_err or ApiExecutionError("Falha na chamada REST dos modelos Gemini.")

    def _generate_stream_via_gemini_api(
        self,
        prompt: str,
        model: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 8192,
        image_path: Optional[str] = None,
    ) -> Iterator[str]:
        """Executa chamada à REST API do Google Gemini (SSE) retornando os chunks de texto via yield."""
        if not self.api_key:
            require_env("GEMINI_API_KEY")

        models_to_try = self._build_model_chain(model)
        parts = self._prepare_parts(prompt, image_path)
        last_err: Optional[Exception] = None

        for current_m in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_m}:streamGenerateContent?alt=sse"
            payload: Dict[str, Any] = {
                "contents": [{"parts": parts}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_output_tokens,
                },
            }
            if system_instruction:
                payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

            try:
                stream_generator = self.google_client.execute_request(
                    method="POST", path_or_url=url, params={"key": self.api_key},
                    data=payload, timeout=35, stream=True,
                )

                def _chunk_generator() -> Iterator[str]:
                    for line in stream_generator:
                        line = line.strip()
                        if not line or not line.startswith("data: "):
                            continue
                        try:
                            data_json = json.loads(line[6:])
                            candidates = data_json.get("candidates", [])
                            if candidates:
                                c_parts = candidates[0].get("content", {}).get("parts", [])
                                if c_parts:
                                    chunk_text = c_parts[0].get("text", "")
                                    if chunk_text:
                                        yield chunk_text
                        except json.JSONDecodeError:
                            pass

                return _chunk_generator()
            except ApiExecutionError as e:
                last_err = e
                if self._is_fallback_worthy_error(e):
                    log("ANTIGRAVITY", f"Modelo {current_m} indisponível para streaming. Tentando fallback...", Colors.YELLOW)
                    continue
                raise e
            except Exception as e:
                wrapped_err = ApiExecutionError(f"Falha de conexão com a API do Gemini ({current_m}): {e}")
                last_err = wrapped_err
                if self._is_fallback_worthy_error(wrapped_err):
                    log("ANTIGRAVITY", f"Falha de rede/streaming no Gemini ({current_m}). Tentando fallback...", Colors.YELLOW)
                    continue
                raise wrapped_err

        raise last_err or ApiExecutionError("Falha na chamada REST dos modelos Gemini (SSE).")
