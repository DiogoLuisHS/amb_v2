# US-57: Sugestão e Auto-Correção de Violações Arquiteturais (amb agy validate --fix)

## 📌 Contexto e Objetivo
O comando `amb agy validate <arquivo>` (ou `amb validate <arquivo>`) audita o código contra as regras canônicas do ecossistema AMB_V2 (ex: limite de 300 linhas, tipagem estrita, isolamento em camadas) e emite um relatório apontando falhas e inconsistências.
Atualmente, após a emissão do diagnóstico, o desenvolvedor é obrigado a efetuar todas as correções manualmente.

Esta US conecta o motor de validação com o modelo cognitivo para propor e aplicar correções imediatas:
```bash
amb agy validate meu_arquivo.py --fix
# ou no validador de stage:
amb validate --staged --fix
```
Quando violações forem detectadas, o motor formula o patch corretivo e solicita confirmação para aplicá-lo diretamente no arquivo.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Módulo de Validação
- **Arquivo (`amb_cli/integrations/antigravity/tools/validate_architecture.py`):**
  - Adicionar a função `generate_architecture_fix(file_path: str, report: str) -> Optional[str]`:
    - Lê o conteúdo original do arquivo e as regras violadas indicadas no `report`.
    - Solicita ao `AntigravityClient` uma correção pontual e cirúrgica do código, preservando a lógica e docstrings originais.
    - Retorna o novo código ajustado ou o diff unificado da alteração.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Integração no Parser e Handler CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - Nos subparsers `validate` (tanto em `antigravity` quanto no top-level `validate`):
    - Adicionar a flag `--fix`:
      ```python
      p.add_argument("--fix", action="store_true", help="Gera e propõe correções automáticas para as violações arquiteturais detectadas.")
      ```
- **Arquivo (`amb_cli/cli_modules/handlers_core/antigravity_handler.py`):**
  - No bloco `sub in ["validate", "audit", "lint"]`:
    - Se `getattr(args, "fix", False)` e `has_violations`:
      - Para cada arquivo com violações:
        - Gerar o patch via `generate_architecture_fix`.
        - Exibir o diff colorido no terminal.
        - Se interativo, solicitar confirmação do usuário `[y/N]` para aplicar as correções no arquivo.
        - Escrever o arquivo atualizado com `encoding="utf-8", errors="replace"`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_antigravity_validate_fix.py` cobrindo:
     - Validação normal sem `--fix` emitindo apenas relatório (preservando comportamento anterior).
     - Validação com `--fix` gerando sugestão de correção via IA em arquivo com violações.
     - Aplicação da correção e verificação de que o arquivo foi atualizado em disco.
     - Parsing adequado da flag `--fix` nos dois locais (`amb agy validate` e `amb validate`).
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
