# US-51: Diagnóstico de Saúde e Conectividade do Runtime Stitch (amb stitch status)

## 📌 Contexto e Objetivo
O Google Stitch SDK depende da presença do runtime Node.js (v18+) no sistema operacional e do pacote oficial `@google/stitch-sdk`, além das credenciais de ambiente (`STITCH_API_KEY` e `STITCH_PROJECT_ID`).
Atualmente, não existe um comando rápido para auditar a integridade desse ambiente: se houver alguma ausência, o desenvolvedor só descobre no meio de uma geração demorada de interface.

Esta US cria o comando dedicado:
```bash
amb stitch status
# ou alias:
amb stitch check
```
Ele avalia e apresenta o diagnóstico completo do ambiente Stitch de forma clara e objetiva.

---

## 📐 Requisitos Técnicos

### 1. Método de Diagnóstico no StitchClient
- **Arquivo (`amb_cli/integrations/stitch/stitch_client.py`):**
  - Implementar o método `get_status(self) -> Dict[str, Any]`:
    - Verifica `shutil.which("node")` e versão do Node (`node -v`).
    - Verifica presença de `STITCH_API_KEY` (configurada ou ausente).
    - Verifica presença de `STITCH_PROJECT_ID`.
    - Verifica existência do runner `stitch_client.mjs`.
    - Se tudo estiver configurado, executa ping leve de listagem de projetos ou telas para validar conectividade e expor status (`connected: True`).
    - Retorna dicionário estruturado com os dados.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Integração no Parser e Handler CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - Adicionar o subcomando `status` com alias `["check"]`:
    ```python
    s = _sc(ss, "status", "Audita a saúde do runtime Node.js, credenciais e conectividade do Stitch SDK.", ["check"])
    _j(s)
    ```
- **Arquivo (`amb_cli/cli_modules/handlers_core/stitch_handler.py`):**
  - Implementar no bloco `sub in ["status", "check"]`:
    - Chamar `client.get_status()`.
    - Se `--json`, imprimir JSON formatado.
    - Caso contrário, imprimir painel visual com cores:
      ```
      === 🎨 DIAGNÓSTICO GOOGLE STITCH SDK ===
        • Node.js Runtime:   Instalado (v20.x)
        • API Key:           Configurada
        • Projeto Ativo:     projects/meu-projeto
        • Conectividade:     Conectada (2 telas ativas)
      ```

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_stitch_status_diagnostic.py` cobrindo:
     - Retorno correto de `client.get_status()` com mocks de Node.js e chaves.
     - Detecção de ausência do Node.js ou de credenciais com alertas visuais.
     - Exibição adequada em texto ANSI e em JSON estruturado (`--json`).
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
