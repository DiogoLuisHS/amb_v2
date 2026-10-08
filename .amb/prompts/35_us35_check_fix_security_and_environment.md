# US-35: Auto-Correção de Ambiente e Segurança em amb check (--fix)

## 📌 Contexto e Objetivo
O comando `amb check` ([`diagnostics.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/core/diagnostics.py)) audita a integridade do workspace e aponta riscos críticos, como o arquivo `.env` não estar protegido no `.gitignore` ou a ausência de `.env.example`. No entanto, o comando atua apenas como alerta passivo, exigindo intervenção manual do desenvolvedor para editar arquivos de configuração.

Esta US implementa a flag `--fix` no comando `amb check`, capacitando o diagnóstico a aplicar correções imediatas e não-destrutivas de segurança e provisionamento básico (como blindagem do `.gitignore` e geração de `.env.example` sanitizado) via [`AmbProvisioner`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/workspace/setup/amb_provisioner.py).

---

## 📐 Requisitos Técnicos

### 1. Mecanismo de Auto-Correção em `diagnostics.py`
- **Arquivo (`amb_cli/core/diagnostics.py`):**
  - No método `run_environment_diagnostics(as_json: bool = False, fix: bool = False, ...)`:
    - Se `fix=True`:
      - Se `env_exists` e `not env_in_gitignore`:
        - Invocará `AmbProvisioner.ensure_gitignore_security(root)`.
        - Atualizará o estado de `env_in_gitignore = True`.
        - Registrará log de correção: `✔ Segurança aplicada: .env adicionado ao .gitignore`.
      - Se `.env.example` não existir:
        - Invocará a geração padrão do template de exemplo.
        - Registrará log de correção: `✔ Template criado: .env.example gerado com sucesso`.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Integração na Camada CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `check`:
    ```python
    p.add_argument("--fix", action="store_true", help="Corrige automaticamente falhas de segurança (.gitignore) e templates ausentes.")
    ```
- **Arquivo (`amb_cli/cli_modules/cli_handlers.py`):**
  - No `cmd_check`: repassar `fix=getattr(args, "fix", False)` para `run_environment_diagnostics(...)`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_check_auto_fix.py` cobrindo:
     - Execução de `amb check` sem `--fix` mantendo o status de alerta inalterado.
     - Execução com `--fix` adicionando `.env` ao `.gitignore` automaticamente em um diretório temporário.
     - Execução com `--fix` criando `.env.example` quando ausente.
     - Garantia de idempotência (múltiplas execuções com `--fix` não duplicam linhas no `.gitignore`).
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
