# 🎯 Tarefa Jules: Auditoria e Alinhamento de `amb_cli/agents/local_agent_runner.py`

## 📌 Arquivo Alvo
- **Caminho:** `amb_cli/agents/local_agent_runner.py`
- **Responsabilidade Única (SRP - Regra 01):** Descobrir e executar personas estáticas do projeto (`.amb/personas/`), despachando para a API do Jules na nuvem ou executando localmente via Google Antigravity SDK / agy CLI.

---

## 📐 Regras Arquiteturais Obrigatórias (`.agents/rules/`)
1. **Regra 01 (SRP):** Foco exclusivo na resolução de diretórios de personas, parsing de metadados das personas markdown e despacho (local via Antigravity ou remoto via Jules).
2. **Regra 02 (Atomização):** Limite estrito de linhas: manter entre 200 e 280 linhas (teto máximo 300).
3. **Regra 03 (DRY & Single Source of Truth):**
   - Resolução de caminhos com prioridade para `.amb/personas/` do projeto ativo.
   - Imports limpos e canônicos (`from config.bootstrap import ensure_amb_env`, `from config import Colors, log, log_error, find_repo_root`).
4. **Regra 04 (Qualidade e Tipagem):**
   - Type hints em 100% das funções: `get_personas_directory(custom_dir: Optional[str] = None) -> str`, `discover_personas(personas_dir: str) -> Dict[str, Dict[str, str]]`, `run_local_agent(...) -> int`.
   - Exceções estruturadas via classe de erro com dicas (`ApiExecutionError(message, hint)`).
5. **Regra 05 (Documentação Concisa):** Docstrings diretas explicando o comportamento da função, sem banners decorativos.
6. **Regra 06 (Segurança e Testes):** Suíte de testes automatizados `pytest` deve permanecer 100% aprovada.

---

## 🛠️ Itens Específicos a Verificar / Refatorar
1. **Resolução de Diretório de Personas:**
   - Garantir prioridade para `.amb/personas/` no repositório ativo com fallback gracioso para `.jules/personas/`.
2. **Tratamento de Execução Local vs Remoto:**
   - Validação da flag `--agy` / `--local` para acionamento do runner Antigravity CLI e verificação defensiva de subprocessos.
3. **Tipagem e Erros:**
   - Tratamento explícito de erros com mensagens contextualizadas e sem captura genérica não rastreável.

---

## 🧪 Validação Obrigatória
Antes de abrir o Pull Request:
```bash
python -m py_compile amb_cli/agents/local_agent_runner.py
python -m pytest
```
Todos os 92 testes unitários devem passar (100% green).

---

## 🚀 Ação Final Obrigatória: Abertura do Pull Request
Ao concluir todas as alterações e validar os testes com sucesso (100% green):
1. Você DEVE submeter/abrir o Pull Request no GitHub imediatamente.
2. Não encerre a sessão apenas no estado "Ready for submission"; confirme a criação do PR diretamente no GitHub com título e descrição claros das alterações.
