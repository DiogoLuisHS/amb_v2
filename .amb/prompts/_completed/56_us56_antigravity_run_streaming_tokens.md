# US-56: Streaming em Tempo Real de Tokens em amb agy run (--stream)

## 📌 Contexto e Objetivo
Ao executar o comando de inferência cognitiva `amb agy run "<prompt>"`, o cliente atual aguarda a geração completa de todo o texto no Gemini antes de imprimir a resposta no terminal.
Para prompts longos, análises ou raciocínios com dezenas de parágrafos, essa espera sem feedback visual no terminal prejudica a experiência interativa do desenvolvedor.

Esta US adiciona suporte a streaming contínuo de tokens em tempo real:
```bash
amb agy run "Explique a evolução da arquitetura REST" --stream
```
Com o texto sendo impresso token a token no terminal à medida que os chunks são recebidos do Gemini.

---

## 📐 Requisitos Técnicos

### 1. Suporte a Streaming no AntigravityClient
- **Arquivo (`amb_cli/integrations/antigravity/antigravity_client.py`):**
  - Adicionar o método `generate_text_stream(self, prompt: str, system_instruction: Optional[str] = None, temperature: float = 0.2)`:
    - Retorna um gerador (`Generator[str, None, None]`) iterando sobre os chunks retornados pela API do Gemini.
    - Suporta tanto a API oficial com SDK quanto requisições HTTP REST com Server-Sent Events / SSE.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Integração no Parser e Handler CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `run` do Antigravity:
    - Adicionar a flag `--stream`:
      ```python
      a.add_argument("--stream", action="store_true", help="Exibe a resposta em tempo real via streaming de tokens.")
      ```
- **Arquivo (`amb_cli/cli_modules/handlers_core/antigravity_handler.py`):**
  - No bloco `sub in ["run", "eval"]`:
    - Se `getattr(args, "stream", False)` e não houver `--output`:
      - Iterar sobre `client.generate_text_stream(...)` imprimindo `chunk` imediatamente com `sys.stdout.write(chunk)` e `sys.stdout.flush()`.
      - Imprimir quebra de linha final ao concluir.
    - Se `--output` for fornecido, acumular o texto gerado e salvar em disco.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_antigravity_run_streaming.py` cobrindo:
     - `generate_text_stream` emitindo chunks progressivos de texto (usando mock).
     - Execução de `amb agy run --stream` escrevendo diretamente em `sys.stdout`.
     - Preservação da execução síncrona padrão quando `--stream` não for passado.
     - Gravação correta do conteúdo completo em arquivo caso `--output` seja informado junto com `--stream`.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
