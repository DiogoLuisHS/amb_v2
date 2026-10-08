# US-54: Leitura Automática de Arquivos de Prompt em amb agy run

## 📌 Contexto e Objetivo
O comando `amb agy run "<prompt>"` permite disparar inferência cognitiva direta com modelos Gemini via terminal. Atualmente, ele aceita apenas texto inline digitado diretamente entre aspas.
Para testar prompts complexos, instruções de sistema longas ou especificações salvas em arquivos locais (ex: `specs/analise.md`), o usuário era obrigado a recorrer a ferramentas de shell para concatenar o conteúdo.

Esta US traz suporte direto e transparente:
```bash
amb agy run specs/prompt_complexo.md
# ou com texto inline normal:
amb agy run "Explique a arquitetura de microsserviços"
```
Se o argumento for um caminho para arquivo existente em disco, seu conteúdo é automaticamente lido e utilizado na inferência. O mesmo comportamento deve se aplicar à flag `--system` (`-s`).

---

## 📐 Requisitos Técnicos

### 1. Atualização do Handler do Antigravity
- **Arquivo (`amb_cli/cli_modules/handlers_core/antigravity_handler.py`):**
  - No bloco `sub in ["run", "eval"]`:
    - Criar função auxiliar interna ou reutilizar:
      ```python
      def _resolve_text_or_file(val: Optional[str]) -> Optional[str]:
          if val and os.path.isfile(val):
              with open(val, "r", encoding="utf-8", errors="replace") as f:
                  return f.read().strip()
          return val
      ```
    - Aplicar na resolução do prompt: `prompt_text = _resolve_text_or_file(getattr(args, "prompt", ""))`
    - Aplicar na resolução da instrução de sistema: `system_text = _resolve_text_or_file(getattr(args, "system", None))`
    - Se `prompt_text` estiver vazio, exibir aviso amigável e retornar.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_antigravity_run_file.py` cobrindo:
     - Execução de inferência com string inline.
     - Execução de inferência passando caminho de arquivo `.md` existente com leitura automática.
     - Suporte a leitura de arquivo na flag `--system` (`-s`).
     - Tratamento gracioso quando o argumento de prompt é omitido.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
