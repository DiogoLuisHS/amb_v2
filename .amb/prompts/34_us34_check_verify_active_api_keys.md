# US-34: Verificação Ativa de Credenciais em amb check (--verify)

## 📌 Contexto e Objetivo
O comando `amb check` ([`diagnostics.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/core/diagnostics.py)) é o ponto central de validação de saúde do ambiente. Contudo, atualmente ele apenas checa se a string da variável de ambiente existe no `.env` (`configured: bool(val)`).

Se a chave de API estiver revogada, expirada ou com formato corrompido, o `amb check` emite falsos positivos (`✅ Configurada`), e a falha só é descoberta minutos depois quando uma sessão no Google Jules ou chamada ao Gemini é disparada na esteira autônoma.

Esta US introduz a flag `--verify` (ou `--probe`) em `amb check`, que realiza um handshake ativo, leve e sem efeitos colaterais com as APIs do Google (Jules e Gemini), atestando a validade real das credenciais antes do início de operações críticas.

---

## 📐 Requisitos Técnicos

### 1. Funções de Probing Leve de Chaves
- **Arquivo (`amb_cli/core/diagnostics.py`):**
  - Adicionar funções de probe não-bloqueantes:
    ```python
    def probe_jules_key(api_key: str) -> Tuple[bool, str]:
        """Realiza requisição GET mínima em /v1alpha/sources?pageSize=1 para validar a chave."""
    ```
    - Se HTTP 200: retorna `(True, "Conectado e autenticado")`.
    - Se HTTP 401/403: retorna `(False, "Chave inválida ou não autorizada")`.
    - Se erro de rede/timeout (timeout máximo 3.0s): retorna `(False, f"Erro de conexão: {err}")`.
    ```python
    def probe_gemini_key(api_key: str) -> Tuple[bool, str]:
        """Valida credencial do Gemini com requisição mínima de modelos ou healthcheck."""
    ```
  - Integrar a execução do probe no loop de `platform_keys` apenas quando `verify=True` for solicitado.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Integração no Relatório Visual e JSON
- **Arquivo (`amb_cli/core/diagnostics.py`):**
  - No formato JSON: incluir `"verified": bool` e `"verify_message": str` dentro de cada item em `platform_keys`.
  - Na saída textual do console:
    - Se `verify=True` e chave válida: `  ✅ Google Jules API: jule...1234 [🌐 Conexão Verificada]`
    - Se `verify=True` e chave inválida: `  ❌ Google Jules API: jule...1234 [🚫 Erro: Chave inválida ou revogada]`

### 3. Integração na CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `check`:
    ```python
    p.add_argument("--verify", "--probe", action="store_true", help="Realiza handshake ativo nas APIs remotas para atestar a validade real das credenciais.")
    ```
- **Arquivo (`amb_cli/cli_modules/cli_handlers.py`):**
  - No `cmd_check`: repassar `verify=getattr(args, "verify", False)` para `run_environment_diagnostics(...)`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_check_verify_keys.py` cobrindo:
     - Execução padrão de `run_environment_diagnostics` sem `--verify` (permanecendo 100% offline).
     - Execução com `verify=True` simulando resposta de sucesso nas APIs (mock 200).
     - Execução com `verify=True` simulando chave revogada (mock 401/403) gerando alerta visual e flag `verified: False`.
     - Tratamento gracioso de timeouts de rede sem quebrar a execução do relatório.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
