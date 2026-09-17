# 🎯 Tarefa Jules: Auditoria e Alinhamento de `amb_cli/agents/monitor.py`

## 📌 Arquivo Alvo
- **Caminho:** `amb_cli/agents/monitor.py`
- **Responsabilidade Única (SRP - Regra 01):** Sentinela e monitor em tempo real das sessões ativas do ecossistema Google (Jules, Stitch, Antigravity), alertando o desenvolvedor e disparando respostas automáticas caso o modo piloto automático (`--auto-approve`) esteja habilitado.

---

## 📐 Regras Arquiteturais Obrigatórias (`.agents/rules/`)
1. **Regra 01 (SRP):** Manter o arquivo focado exclusivamente na coordenação do ciclo de vigilância e delegação ao `JulesWatcher` e `advise_and_reply`.
2. **Regra 02 (Atomização):** Manter o arquivo granular e conciso (em torno de 90 a 150 linhas, teto máximo 300).
3. **Regra 03 (DRY & Imports Canônicos):**
   - Importar `advise_and_reply` no topo do arquivo (`from agents.auto_reply import advise_and_reply`), proibindo imports dinâmicos tardios dentro de loops de repetição.
   - Imports limpos do pacote: `from integrations.jules.jules_watcher import JulesWatcher`, `from cli_modules.alert_notifier import notify_info`.
4. **Regra 04 (Qualidade e Tipagem):**
   - Assinaturas tipadas: `run_monitor(interval_seconds: int = 15, check_once: bool = False, auto_approve: bool = False) -> None`, `UnifiedMonitor.run(check_once: bool = False) -> None`, `main() -> None`.
5. **Regra 05 (Documentação Concisa):** Eliminar comentários supérfluos e manter docstring declarativa no cabeçalho e nos métodos.
6. **Regra 06 (Segurança e Testes):** Garantir que `pytest` passe com 100% de sucesso.

---

## 🛠️ Itens Específicos a Verificar / Refatorar
1. **Eliminação de Dead Imports:**
   - Garantir que imports mortos (`argparse`, `sys`, `os`) não estejam presentes no arquivo.
2. **Tratamento de Exceções & Loop de Polling:**
   - Assegurar que falhas de rede transitórias no watcher não derrubem o processo de monitoramento e sejam logadas via `log_error`.
   - Garantir encerramento limpo em caso de `KeyboardInterrupt`.

---

## 🧪 Validação Obrigatória
Antes de abrir o Pull Request:
```bash
python -m py_compile amb_cli/agents/monitor.py
python -m pytest
```
Todos os 92 testes unitários devem passar (100% green).
