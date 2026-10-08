# US-45: Re-execução Instantânea de Tarefas do Jules (amb jules rerun <id>)

## 📌 Contexto e Objetivo
Conforme documentado oficialmente pelo Google Jules em `/docs/errors/`, falhas podem ocorrer devido a timeouts na VM, dependências de rede temporárias ou interrupções. Atualmente no AMB_V2, quando uma sessão falha ou precisa ser reiniciada, o desenvolvedor é obrigado a:
1. Buscar os detalhes da sessão antiga via `amb jules get <id>`;
2. Copiar manualmente o prompt original, branch e título;
3. Executar manualmente `amb jules create -p "..." -b "..." -t "..."`.

Esta US implementa o comando de re-execução instantânea:
```bash
amb jules rerun <session_id>
# ou o alias:
amb jules restart <session_id>
```
O comando recupera os metadados da sessão original diretamente via API e dispara imediatamente uma nova sessão correspondente na nuvem do Jules.

---

## 📐 Requisitos Técnicos

### 1. Ferramenta de Re-execução
- **Arquivo (`amb_cli/integrations/jules/tools/rerun_session.py`):**
  - Implementar `run_rerun_session(session_id: str, new_prompt: Optional[str] = None, new_branch: Optional[str] = None, as_json: bool = False) -> dict`:
    1. Instanciar `JulesClient` e buscar a sessão alvo via `get_session(clean_id)`.
    2. Extrair o prompt da sessão:
       - Tentar ler de `sess.get("prompt")` ou inspecionar as primeiras mensagens das atividades (`list_activities`).
       - Se `new_prompt` foi fornecido na CLI, sobrescrever o prompt original.
    3. Extrair a branch base (`sourceContext.gitContext.targetBranch`) e o título da sessão (`sess.get("title")`).
       - Se `new_branch` foi fornecido na CLI, sobrescrever.
    4. Adicionar marcação descritiva ao título: `f"[Rerun] {old_title}"`.
    5. Chamar `run_create_session` com os metadados recuperados.
    6. Exibir no terminal o ID da nova sessão criada e o link para acompanhamento.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Integração no Parser e Handler CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `jules`:
    - Adicionar o subcomando `rerun` com alias `["restart"]`:
      ```python
      j = _sc(js, "rerun", "Recria e reinicia uma sessão anterior preservando prompt e contexto.", ["restart"])
      _sid(j, "ID ou URL da sessão original do Jules a ser reiniciada.")
      j.add_argument("--prompt", "-p", help="Sobrescreve o prompt original da sessão.")
      j.add_argument("--branch", "-b", help="Sobrescreve a branch original da sessão.")
      _j(j)
      ```
- **Arquivo (`amb_cli/cli_modules/handlers_core/jules_handler.py`):**
  - Incluir no roteamento:
    ```python
    elif sub in ["rerun", "restart"]:
        sid = getattr(args, "session_id", None) or getattr(args, "session_id_flag", None)
        if not sid:
            log_error("JULES", "Informe o ID da sessão a ser reiniciada.")
            return
        from integrations.jules.tools.rerun_session import run_rerun_session
        run_rerun_session(
            session_id=sid,
            new_prompt=getattr(args, "prompt", None),
            new_branch=getattr(args, "branch", None),
            as_json=getattr(args, "json", False)
        )
    ```

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_jules_rerun.py` cobrindo:
     - Re-execução com recuperação automática de prompt, branch e título da sessão anterior.
     - Sobrescrita de prompt e branch caso fornecidos via parâmetros na linha de comando.
     - Criação da nova sessão com retorno de ID e link da VM.
     - Tratamento gracioso quando a sessão original não é encontrada (404 / NOT_FOUND).
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
