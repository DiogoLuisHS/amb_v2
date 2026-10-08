# US-39: Vigilância Multi-Repositório na Conta Google Jules (amb monitor --all)

## 📌 Contexto e Objetivo
Atualmente, o sentinela [`JulesWatcher`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/integrations/jules/jules_watcher.py) é instanciado restringindo a vigilância estritamente ao repositório Git local ativo:
```python
repo = get_repo_name()
sessions = self.client.list_sessions(page_size=30, repo_filter=repo)
```
Em monorepos, arquiteturas de microsserviços ou quando o desenvolvedor executa tarefas em múltiplos projetos simultaneamente, o sentinela ignora completamente qualquer sessão que pertença a outro repositório conectado à mesma conta do Jules. O desenvolvedor é forçado a abrir múltiplos terminais em cada diretório de projeto.

Esta US adiciona a flag `--all` (ou `--all-repos`) ao comando `amb monitor`, permitindo que uma única instância do sentinela vigie, notifique e auto-responda todas as sessões ativas da conta Google Jules globalmente.

---

## 📐 Requisitos Técnicos

### 1. Suporte a Multi-Repo no `JulesWatcher`
- **Arquivo (`amb_cli/integrations/jules/jules_watcher.py`):**
  - Atualizar o construtor:
    ```python
    def __init__(self, client: Optional[JulesClient] = None, all_repos: bool = False):
        self.client = client or ...
        self.all_repos = all_repos
        self.notified_events = set()
    ```
  - No método `check()`:
    - Se `self.all_repos`: definir `repo_filter = None`.
    - Caso contrário: manter `repo_filter = get_repo_name()`.
    - Invocar `self.client.list_sessions(page_size=50, repo_filter=repo_filter)`.
    - Nas mensagens de alerta de atenção, prefixar com o identificador da fonte/repositório caso `all_repos` esteja ativo:
      `[owner/repo] Sessão aguardando sua resposta: '{title}'`
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Integração no `UnifiedMonitor` e `run_monitor`
- **Arquivo (`amb_cli/agents/monitor.py`):**
  - Atualizar `run_monitor` e `UnifiedMonitor` para aceitar `all_repos: bool = False`.
  - Instanciar `JulesWatcher(all_repos=all_repos)`.
  - No banner de inicialização, exibir:
    `Escopo:              🌐 Todos os repositórios da conta` se `all_repos` for True, ou `📁 Repositório local ({get_repo_name()})`.

### 3. Integração na Camada CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `monitor`:
    ```python
    p.add_argument("--all", "--all-repos", dest="all_repos", action="store_true", help="Vigia sessões de todos os repositórios conectados à conta Jules (desativa o filtro local).")
    ```
- **Arquivo (`amb_cli/cli_modules/cli_handlers.py`):**
  - No `cmd_monitor`: repassar `all_repos=getattr(args, "all_repos", False)`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_monitor_all_repos.py` cobrindo:
     - Instanciação de `JulesWatcher(all_repos=True)` consultando `list_sessions(repo_filter=None)`.
     - Instanciação padrão com `all_repos=False` preservando o filtro pelo repositório local.
     - Formatação de alertas incluindo o nome do repositório no modo multi-repo.
     - Parsing da flag `--all` / `--all-repos` no subparser de `amb monitor`.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
