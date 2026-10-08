# US-29: Inspeção Estruturada de Comandos Bash na VM (bashOutput)

## 📌 Contexto e Objetivo
A documentação de tipos da API REST do Google Jules (`https://jules.google/docs/api/reference/types`) define que os artefatos de atividades gerados pelo Jules podem conter comandos de terminal executados na VM do Cloud (`bashOutput`):
```json
{
  "bashOutput": {
    "command": "pytest -q",
    "output": "246 passed in 4.28s",
    "exitCode": 0
  }
}
```

No AMB_V2, o comando `amb jules extract <session_id>` extrai exclusivamente o patch unificado de Git (`gitPatch`). Quando uma sessão falha ou quando o desenvolvedor quer entender exatamente quais comandos o Jules rodou (ex: se executou `pip install`, se rodou os testes locais, qual foi o `exitCode` exato do linter), é necessário abrir o console web.

Esta US estende o [`SessionExtractor`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/integrations/jules/jules_core/session_extractor.py) com a extração de saídas de bash e adiciona a flag `--bash` em `amb jules extract <session_id>` para inspecionar localmente o histórico de execução de comandos na VM.

---

## 📐 Requisitos Técnicos

### 1. Método `extract_bash_outputs` em `SessionExtractor`
- **Arquivo (`amb_cli/integrations/jules/jules_core/session_extractor.py`):**
  - Adicionar o método estático:
    ```python
    @staticmethod
    def extract_bash_outputs(activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extrai todos os artefatos de bashOutput das atividades da sessão.
        Retorna lista de dicionários com 'command', 'output' e 'exitCode'.
        """
    ```
  - Iterar por todas as atividades e seus respectivos `artifacts`.
  - Para cada artefato que contenha `bashOutput`:
    - Adicionar ao resultado o dicionário estruturado:
      `{"command": b.get("command", ""), "output": b.get("output", ""), "exitCode": b.get("exitCode", 0)}`.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Exibição no Comando `amb jules extract`
- **Arquivo (`amb_cli/integrations/jules/tools/extract_session.py`):**
  - Atualizar `run_extract_session` para aceitar `show_bash: bool = False`:
    ```python
    def run_extract_session(
        session_id: str,
        dest_path: Optional[str] = None,
        apply: bool = False,
        show_bash: bool = False,
        client: Optional[JulesClient] = None
    ) -> None:
    ```
  - Se `show_bash` for True:
    - Buscar as atividades da sessão via `client.list_activities(clean_id)`.
    - Chamar `bash_list = SessionExtractor.extract_bash_outputs(activities)`.
    - Exibir título: `=== 🖥️ COMANDOS BASH EXECUTADOS NA VM ===`.
    - Se vazio, exibir: `Nenhum comando bash registrado nos artefatos desta sessão.`
    - Se houver comandos, iterar exibindo:
      - `[$] {command}` (com cor verde se `exitCode == 0`, vermelho se `!= 0`)
      - `    Status: exit {exitCode}`
      - `    Saída:\n{output}`

### 3. Integração na Camada CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `extract`:
    ```python
    j.add_argument("--bash", action="store_true", help="Lista e exibe todos os comandos bash executados pelo Jules na VM com status e saídas.")
    ```
- **Arquivo (`amb_cli/cli_modules/handlers_core/jules_handler.py`):**
  - No bloco `sub == "extract"`:
    - Repassar `show_bash=getattr(args, "bash", False)` para `run_extract_session(...)`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_extract_bash_outputs.py` cobrindo:
     - Extração correta de artefatos com `bashOutput` a partir de uma lista de atividades.
     - Retorno de lista vazia quando nenhuma atividade contém `bashOutput`.
     - Exibição formatada no terminal com comando, saída e exit code.
     - Parsing da flag `--bash` no CLI parser de `amb jules extract`.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
