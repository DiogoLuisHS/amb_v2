# US-44: Diagnóstico Padrão ao Executar amb jules sem Subcomando

## 📌 Contexto e Objetivo
Atualmente, quando o desenvolvedor executa `amb jules` no terminal sem passar nenhum subcomando, o sistema emite uma mensagem de erro genérica:
```
Subcomando do Jules inválido. Use 'amb jules --help'.
```
Essa resposta é improdutiva. O comportamento natural e ágil para o comando raiz de uma integração deve ser exibir imediatamente o diagnóstico geral de conectividade, saúde de chaves, repositório ativo e contagem de sessões (`amb jules status`), economizando tempo e comandos extras.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Handler Central do Jules
- **Arquivo (`amb_cli/cli_modules/handlers_core/jules_handler.py`):**
  - No início de `handle_cmd_jules`:
    - Se `sub is None` ou `not sub`:
      - Tratar automaticamente como `status`:
        ```python
        sub = "status"
        ```
  - Isso faz com que a execução de `amb jules` exiba o painel formatado de diagnóstico:
    ```
    === ☁️ DIAGNÓSTICO GOOGLE JULES ===
      • API Key:           Configurada
      • API REST:          Conectada
      • Fontes na Conta:   ...
      • Repositório Alvo:  ...
      • Sessões do Repo:   Total: ... | Aguardando: ... | Concluídas: ...
    ```

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_jules_default_status.py` cobrindo:
     - Chamada a `handle_cmd_jules` com `args.jules_cmd = None` disparando a exibição de diagnóstico do `JulesClient`.
     - Preservação da flag `--json` se fornecida junto a `amb jules`.
     - Garantia de que subcomandos inválidos desconhecidos continuam exibindo instrução de ajuda.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
