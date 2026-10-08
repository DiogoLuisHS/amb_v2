# US-75: Limpeza de Flags Mortas e Comportamentos Padrão Amigáveis nos Orquestradores

## 📌 Contexto e Objetivo
Ao longo da evolução da CLI, algumas flags e comandos acumularam ambiguidades e comportamentos pouco ergonômicos:
1. **Flag Legada Inútil:** No subparser `agent`, existe a flag `--dispatch-jules` (`-j`), documentada como legada. O despacho para o Jules já é o comportamento padrão desde a primeira versão da CLI. Essa flag polui o `--help`.
2. **Conflito de Aliases `-c`:** O alias `-c` colidia entre `--loop` / `--continuous` e `--concurrency`.
3. **Erros Secos em Invocação Nua:** Executar `amb loop` sem argumentos causava aborto com `sys.exit(1)`, enquanto `amb persona` sem argumentos exibia erro de subcomando ausente.

Esta US limpa e moderniza a interface de linha de comando:
- Remove a flag morta `--dispatch-jules`.
- Reserva o alias curto `-c` exclusivamente para `--concurrency <N>` no processamento em lote.
- Padroniza `--loop` e `--continuous` para ciclos contínuos sem ambiguidades.
- Define que invocar `amb loop` sem argumentos executa automaticamente `status`.
- Define que invocar `amb persona` sem argumentos executa automaticamente a listagem de personas com badges de validação estrutural (`✅ Válida` ou `⚠️ Incompleta`).

---

## 📐 Requisitos Técnicos

### 1. Atualização dos Parsers CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `agent`:
    - Remover completamente a flag `--dispatch-jules` / `-j`.
    - Garantir que `--concurrency` use `-c`.
    - Garantir que `--loop` e `--continuous` estejam definidos sem colisão com `-c`.
  - No subparser `persona`:
    - Adicionar o subcomando `list`:
      ```python
      _sc(ps, "list", "Lista todas as personas locais com status de validação arquitetural.")
      ```

### 2. Atualização dos Handlers
- **Arquivo (`amb_cli/cli_modules/handlers_core/loop_handler.py`):**
  - Se `not sub_cmd`:
    - Tratar automaticamente como `"status"` em vez de emitir erro com `sys.exit(1)`.
- **Arquivo (`amb_cli/cli_modules/handlers_core/persona_handler.py`):**
  - Se `not hasattr(args, "persona_cmd")` ou `args.persona_cmd in [None, "list"]`:
    - Executar listagem e validação das personas locais com exibição formatada.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_orchestrator_clean_defaults.py` cobrindo:
     - Invocação de `amb loop` sem argumentos exibindo o status da máquina finita com sucesso.
     - Invocação de `amb persona` sem argumentos listando personas locais com badges de validação.
     - Verificação de ausência de `--dispatch-jules` no parser.
     - Parsing inequívoco de `--concurrency -c 3` e `--loop`.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
