# US-50: Abertura Direta de Telas no Navegador (amb stitch view <id> e flag --open)

## 📌 Contexto e Objetivo
O Google Stitch gera screenshots visuais e código HTML de telas. Atualmente, após gerar (`generate`), consultar (`get`) ou refinar (`refine`) uma tela, o desenvolvedor precisa copiar manualmente a URL da screenshot no terminal ou procurar o arquivo HTML em disco para abrir no navegador.

Esta US elimina esse atrito visual proporcionando feedback instantâneo:
1. **Subcomando Direto `amb stitch view <screen_id>`:** Consulta a tela e abre imediatamente o screenshot ou o HTML gerado no navegador padrão do sistema operacional via `webbrowser.open()`.
2. **Flag `--open` em `generate`, `refine` e `get`:** Ao finalizar a operação com sucesso, abre automaticamente a visualização gráfica no navegador caso a flag `--open` seja passada.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - Adicionar o subcomando `view`:
    ```python
    s = _sc(ss, "view", "Abre a screenshot ou HTML da tela diretamente no navegador padrão.")
    s.add_argument("screen_id", help="ID da tela a ser visualizada.")
    _j(s)
    ```
  - Nos subparsers `generate`, `refine` e `get`, adicionar a flag `--open`:
    ```python
    s.add_argument("--open", action="store_true", help="Abre o resultado visual no navegador automaticamente após concluir.")
    ```

### 2. Atualização do Handler
- **Arquivo (`amb_cli/cli_modules/handlers_core/stitch_handler.py`):**
  - Importar `import webbrowser`.
  - Criar função utilitária interna:
    ```python
    def _open_in_browser(res: dict, output_file: Optional[str] = None) -> None:
        url = res.get("screenshotUrl")
        if output_file and os.path.exists(output_file):
            webbrowser.open(f"file://{os.path.abspath(output_file)}")
        elif url:
            webbrowser.open(url)
    ```
  - Implementar o subcomando `view`:
    - Executa `client.get_screen(screen_id=args.screen_id)`.
    - Chama `_open_in_browser(res)`.
  - Nos blocos `generate`, `refine` e `get`:
    - Se `getattr(args, "open", False)`:
      - Invocar `_open_in_browser(res, output_file)`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_stitch_view_open.py` cobrindo:
     - Subcomando `amb stitch view <id>` disparando `webbrowser.open` com a URL da screenshot ou caminho do HTML (usando mock).
     - Execução de `generate` com `--open` invocando a abertura no browser.
     - Execução normal sem `--open` não invocando o navegador.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
