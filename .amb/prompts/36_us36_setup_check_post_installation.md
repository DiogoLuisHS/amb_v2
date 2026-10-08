# US-36: Validação Integrada de Ambiente Pós-Setup (amb setup --check)

## 📌 Contexto e Objetivo
Ao concluir a análise de projeto e o provisionamento da pasta `.amb/`, o assistente `amb setup` ([`setup_project.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/workspace/setup/setup_project.py)) imprime no terminal a lista de próximos passos:
```
👉 Próximos passos recomendados:
   • Validar ambiente: amb check
```
Essa separação obriga o desenvolvedor ou pipelines de CI a invocarem um segundo comando manual (`amb check`) apenas para conferir se o setup foi bem-sucedido e se as variáveis mínimas estão presentes.

Esta US adiciona a flag `--check` (ou `-c`) ao comando `amb setup`, encadeando automaticamente a execução do diagnóstico de ambiente logo após a conclusão do provisionamento, oferecendo uma experiência de inicialização unificada e completa em um único comando.

---

## 📐 Requisitos Técnicos

### 1. Parâmetro e Encadeamento em `setup_project.py`
- **Arquivo (`amb_cli/workspace/setup/setup_project.py`):**
  - Atualizar a assinatura de `run_setup`:
    ```python
    def run_setup(
        interactive: bool = True,
        target_dir: Optional[str] = None,
        force: bool = False,
        dry_run: bool = False,
        run_check: bool = False
    ) -> Dict[str, Any]:
    ```
  - Após a conclusão do provisionamento e antes do retorno final:
    - Se `run_check` for True:
      - Emitir cabeçalho: `\n🔍 Executando diagnóstico integrado pós-setup...\n`
      - Importar e invocar:
        ```python
        from core.diagnostics import run_environment_diagnostics
        run_environment_diagnostics(as_json=False)
        ```
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Integração na CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `setup`:
    ```python
    p.add_argument("--check", "-c", action="store_true", help="Executa o diagnóstico de saúde (amb check) automaticamente ao concluir o setup.")
    ```
- **Arquivo (`amb_cli/cli_modules/cli_handlers.py`):**
  - No `cmd_setup`: repassar `run_check=getattr(args, "check", False)` para `run_setup(...)`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_setup_check_integration.py` cobrindo:
     - Execução padrão de `run_setup` sem `run_check` (não invoca o diagnóstico).
     - Execução com `run_check=True` invocando `run_environment_diagnostics` com sucesso.
     - Parsing da flag `--check` no parser de CLI de `amb setup`.
     - Resiliência quando executado em modo `--dry-run`.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
