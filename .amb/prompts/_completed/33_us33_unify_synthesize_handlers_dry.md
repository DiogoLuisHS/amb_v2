# US-33: Unificação dos Handlers de Síntese e Eliminação de Mutações de Argumentos (DRY)

## 📌 Contexto e Objetivo
Atualmente, a execução do comando `amb prompt` realiza uma delegação com mutação artificial do objeto de argumentos CLI em [`cli_handlers.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/cli_modules/cli_handlers.py#L27-L37):
```python
def cmd_prompt(args: Any) -> None:
    if getattr(args, "synthesize", None):
        from cli_modules.handlers_core.antigravity_handler import handle_cmd_antigravity
        args.agy_cmd = "prompt"
        args.idea = args.synthesize
        handle_cmd_antigravity(args)
```
Essa abordagem viola os princípios de baixo acoplamento e separação de camadas:
1. Injeta propriedades dinâmicas (`agy_cmd`, `idea`) no namespace do `argparse`.
2. Acopla o comando global `prompt` ao despachante interno `handle_cmd_antigravity`.
3. Inconsistência de flags: `amb prompt` utiliza `--synthesize` e `--image`, enquanto `amb antigravity prompt` utiliza `--idea` e ignora mocks de imagem.

Esta US elimina a mutação mágica de estado e unifica a invocação direta da função de domínio `run_synthesize_prompt`, padronizando as assinaturas e garantindo conformidade estrita com o princípio DRY (Regra 03).

---

## 📐 Requisitos Técnicos

### 1. Chamada Direta e Tipada em `cmd_prompt`
- **Arquivo (`amb_cli/cli_modules/cli_handlers.py`):**
  - No método `cmd_prompt`:
    - Extrair parâmetros de forma limpa:
      ```python
      idea = getattr(args, "idea", None) or getattr(args, "synthesize", None)
      role = getattr(args, "role", "general")
      output_file = getattr(args, "output", None)
      image_path = getattr(args, "image", None)
      ```
    - Importar e invocar diretamente:
      ```python
      from integrations.antigravity.tools.synthesize_prompt import run_synthesize_prompt
      run_synthesize_prompt(
          raw_idea=idea,
          role=role,
          output_file=output_file,
          image_path=image_path
      )
      ```
    - Remover completamente a dependência de `handle_cmd_antigravity` e mutação de `args.agy_cmd`.

### 2. Padronização em `antigravity_handler.py`
- **Arquivo (`amb_cli/cli_modules/handlers_core/antigravity_handler.py`):**
  - No bloco `sub in ["prompt", "synthesize", "synth"]`:
    - Extrair `idea = getattr(args, "idea", None) or getattr(args, "synthesize", None)`.
    - Garantir que `--image` seja repassado para `run_synthesize_prompt` se presente.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 3. Alinhamento no Parser de CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `antigravity prompt`:
    - Adicionar argumento `--image` / `-img` para permitir síntese multimodal também via `amb antigravity prompt`.
    - Aceitar `--synthesize` como alias para `--idea`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_synthesize_handlers_unification.py` cobrindo:
     - Chamada a `cmd_prompt` invocando `run_synthesize_prompt` diretamente sem modificar o objeto `args`.
     - Invocação de `handle_cmd_antigravity` com repasse de imagem e ideia.
     - Garantia de que nenhuma chave espúria (`agy_cmd`) é injetada em `args`.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
