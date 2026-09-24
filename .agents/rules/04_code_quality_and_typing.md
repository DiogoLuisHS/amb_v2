# 🛡️ Regra 04: Qualidade de Código, Tipagem Estrita e Tratamento de Erros

> **Escopo:** Padrões de Código Python, Assinaturas de Métodos e Resiliência  
> **Objetivo:** Garantir robustez estática, contratos de tipo determinísticos e tratamento defensivo de exceções em todo o ecossistema.

---

## 1. Tipagem Estrita Obrigatória (Type Hints)

- **Assinaturas Completas:** Toda função ou método público deve declarar os tipos de todos os seus argumentos e do valor de retorno.
- **Tipos Canônicos:** Utilizar o módulo `typing` do Python (`Optional`, `Union`, `List`, `Dict`, `Any`, `Tuple`) e `pathlib.Path`:
  ```python
  def execute_command(
      cmd: Union[str, List[str]], 
      cwd: Optional[Path] = None, 
      timeout_seconds: int = 60
  ) -> Dict[str, Any]:
  ```
- **Proibição de Tipos Implícitos:** Evitar funções sem anotação de retorno (`-> None`, `-> bool`, etc.) para permitir análise estática pelo IDE e ferramentas de lint.

---

## 2. Hierarquia de Exceções e Princípio Fail-Fast

- **Hierarquia Canônica `AmbError`:** Todas as exceções do AMB_V2 devem herdar de `AmbError` (definida em `amb_cli/core/exceptions.py`):
  - `ConfigurationError`: Falha em variáveis de ambiente, dependências ou arquivos ausentes.
  - `ApiError`: Falha em chamadas de API externas (HTTP 4xx/5xx, timeouts).
  - `GitError`: Falha em comandos locais do Git ou GitHub CLI.
- **Fail-Fast com Mensagens Acionáveis:**
  - Validar pré-requisitos antes de iniciar operações longas.
  - Se uma chave obrigatória não estiver presente, disparar `require_env(...)` imediatamente com orientação clara sobre como resolver (ex: `"Adicione ao .env ou exporte JULES_API_KEY"`).
- **Proibido Mascarar Erros:**
  - Nunca utilizar blocos `except: pass` vazios.
  - Nunca capturar `Exception` de forma genérica sem registrar o erro com `log_error(...)` ou relançá-lo com contexto.

---

## 3. Saída Estruturada e Suporte a `--json`

- Todas as ferramentas CLI e funções de serviço devem suportar a flag `--json`.
- Quando `--json` for especificado, a ferramenta deve imprimir **exclusivamente** JSON válido na saída padrão (stdout), sem poluir com banners de texto ou logs intermediários.
- A saída estruturada viabiliza a orquestração por agentes de IA e scripts de CI/CD.
