#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente Base Padronizado para APIs Google (F1-M2)
Localização: amb_v2/integrations/common/base_google_client.py
Responsabilidade Única: Prover fundação HTTP resiliente para integrações Google
(Jules, Gemini/Antigravity, Stitch, etc.), com retry automático com backoff exponencial
e jitter, normalização semântica de erros (ApiExecutionError) e mascaramento de credenciais.
"""

import json
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Set

from core import ApiExecutionError, Colors, log, log_error


def mask_sensitive_data(text: str) -> str:
    """Mascara credenciais e tokens em strings para prevenir vazamento em logs."""
    if not text or not isinstance(text, str):
        return text

    # Mascara chaves estilo AIzaSy... mantendo os primeiros 6 caracteres e últimos 4
    def _mask_aiza(match: re.Match) -> str:
        val = match.group(0)
        if len(val) > 10:
            return f"{val[:6]}...{val[-4:]}"
        return "AIzaSy****"

    masked = re.sub(r"AIzaSy[A-Za-z0-9_-]{20,}", _mask_aiza, text)

    # Mascara query parameters key=...
    masked = re.sub(r"(key=)[A-Za-z0-9_-]+", r"\1****", masked)

    # Mascara headers X-Goog-Api-Key e Authorization
    masked = re.sub(r"(X-Goog-Api-Key:\s*)[^\r\n,]+", r"\1****", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(Bearer\s+)[A-Za-z0-9_.-]+", r"\1****", masked, flags=re.IGNORECASE)

    return masked


class BaseGoogleClient:
    """Cliente HTTP base e resiliente para APIs do ecossistema Google."""

    DEFAULT_RETRY_STATUSES: Set[int] = {429, 500, 502, 503, 504}

    def __init__(
        self,
        base_url: str = "",
        api_key: Optional[str] = None,
        timeout: int = 40,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 16.0,
        service_name: str = "GOOGLE",
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.service_name = service_name

    def _calculate_backoff_delay(self, attempt: int) -> float:
        """Calcula o tempo de espera com backoff exponencial e jitter (0.8x a 1.2x)."""
        calc = min(self.max_delay, self.base_delay * (2 ** (attempt - 1)))
        jitter = 0.8 + 0.4 * random.random()
        return max(0.1, calc * jitter)

    def _normalize_error(
        self,
        error: Exception,
        status_code: Optional[int] = None,
        error_body: Optional[str] = None,
    ) -> ApiExecutionError:
        """Converte exceções HTTP e de rede em ApiExecutionError com mensagens e dicas claras."""
        msg = f"Falha de conexão com {self.service_name}: {error}"
        hint = "Verifique sua conexão com a internet ou proxy local."

        if status_code is not None:
            clean_body = error_body or ""
            detail = ""
            try:
                err_json = json.loads(clean_body)
                if "error" in err_json:
                    err_obj = err_json["error"]
                    if isinstance(err_obj, dict):
                        detail = err_obj.get("message") or clean_body
                    elif isinstance(err_obj, str):
                        detail = err_obj
            except Exception:
                detail = clean_body.strip()

            msg = f"HTTP {status_code} na API {self.service_name}"
            if detail:
                msg = f"{msg} - {detail}"

            if status_code in (401, 403):
                hint = (
                    f"Acesso negado ou credencial inválida. "
                    f"Verifique se a chave de API é válida e possui permissões ativas para {self.service_name}."
                )
            elif status_code == 404:
                hint = "Recurso não encontrado. Verifique o ID do recurso ou caminho do endpoint."
            elif status_code == 429:
                hint = (
                    "Limite de quota excedido (Rate Limit). "
                    "Aguarde alguns instantes para renovação da quota por minuto no Google Cloud."
                )
            elif status_code in (500, 502, 503, 504):
                hint = (
                    "Instabilidade temporária nos servidores do Google. "
                    "Tente novamente em instantes."
                )
            elif status_code == 400:
                hint = "Requisição malformada. Verifique a estrutura do payload JSON e os parâmetros enviados."

        safe_msg = mask_sensitive_data(msg)
        return ApiExecutionError(safe_msg, hint=hint)

    def execute_request(
        self,
        method: str,
        path_or_url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        retry_statuses: Optional[Set[int]] = None,
    ) -> Dict[str, Any]:
        """Executa uma requisição HTTP autenticada com resiliência, retry e decodificação JSON."""
        # 1. Resolve URL completa
        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            url = path_or_url
        else:
            url = f"{self.base_url}/{path_or_url.lstrip('/')}"

        if params:
            query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            url = f"{url}?{query}" if "?" not in url else f"{url}&{query}"

        # 2. Configura Headers
        req_headers = {
            "Content-Type": "application/json",
            "User-Agent": "AMB-CLI-v2/1.0",
        }
        if self.api_key:
            req_headers["X-Goog-Api-Key"] = self.api_key
        if headers:
            req_headers.update(headers)

        body_bytes = json.dumps(data).encode("utf-8") if data is not None else None
        retries_limit = self.max_retries if max_retries is None else max_retries
        req_timeout = self.timeout if timeout is None else timeout
        effective_retry_statuses = retry_statuses or self.DEFAULT_RETRY_STATUSES

        last_error: Optional[Exception] = None

        for attempt in range(1, retries_limit + 1):
            req = urllib.request.Request(
                url,
                data=body_bytes,
                headers=req_headers,
                method=method.upper(),
            )
            try:
                with urllib.request.urlopen(req, timeout=req_timeout) as resp:
                    resp_text = resp.read().decode("utf-8")
                    return json.loads(resp_text) if resp_text.strip() else {}
            except urllib.error.HTTPError as e:
                error_body = ""
                try:
                    error_body = e.read().decode("utf-8")
                except Exception:
                    pass

                # Se for código com direito a retry e ainda restarem tentativas
                if e.code in effective_retry_statuses and attempt < retries_limit:
                    delay = self._calculate_backoff_delay(attempt)
                    masked_url = mask_sensitive_data(url)
                    log(
                        self.service_name,
                        f"Instabilidade transitória (HTTP {e.code}) em {masked_url}. "
                        f"Tentativa {attempt}/{retries_limit}. Aguardando {delay:.2f}s...",
                        Colors.YELLOW,
                    )
                    time.sleep(delay)
                    continue

                raise self._normalize_error(e, status_code=e.code, error_body=error_body)

            except (urllib.error.URLError, TimeoutError) as e:
                last_error = e
                if attempt < retries_limit:
                    delay = self._calculate_backoff_delay(attempt)
                    log(
                        self.service_name,
                        f"Falha de rede/timeout ({e}). Tentativa {attempt}/{retries_limit}. "
                        f"Aguardando {delay:.2f}s...",
                        Colors.YELLOW,
                    )
                    time.sleep(delay)
                    continue
                raise self._normalize_error(e)
            except Exception as e:
                raise self._normalize_error(e)

        if last_error:
            raise self._normalize_error(last_error)
        raise ApiExecutionError(f"Falha ao executar requisição na API {self.service_name}.")
