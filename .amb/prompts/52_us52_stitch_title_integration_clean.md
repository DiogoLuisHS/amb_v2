# US-52: Tratamento e Incorporação Semântica de Título de Telas no Stitch

## 📌 Contexto e Objetivo
No subcomando `amb stitch generate`, o parser aceita a flag `--title` / `-t`:
```python
s.add_argument("--title", "-t", help="Título da tela.")
```
Porém, no fluxo atual, esse valor era silenciosamente descartado tanto no `stitch_handler.py` quanto no `stitch_client.py`, criando um "parâmetro fantasma" que engana o usuário.

Seguindo o princípio de design limpo e sem código morto:
1. Se `--title` (ou `-t`) for fornecido, ele deve ser efetivamente incorporado na solicitação de geração da tela:
   - Injetado no prompt visual de forma semântica estruturada: `f"Title: {title}\nSpecification: {prompt}"`
   - Salvo no metadado do HTML de saída como `<title>{title}</title>`.
2. Se `--output` não for informado mas `--title` for, sugere e define um nome de arquivo amigável baseado no título (ex: `specs/{slug}.html`).

---

## 📐 Requisitos Técnicos

### 1. Atualização do StitchClient
- **Arquivo (`amb_cli/integrations/stitch/stitch_client.py`):**
  - Atualizar o método `generate_screen`:
    ```python
    def generate_screen(
        self,
        prompt: str,
        title: Optional[str] = None,
        device_type: Optional[str] = None,
        model_id: Optional[str] = None,
        design_system: Optional[str] = None,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
    ```
  - Se `title`:
    - Incorporar `title` no prompt enviado ao SDK ou repassar `title` no payload caso o runner suporte.
    - Se `res.get("htmlCode")` existir e contiver `<title>`, garantir que a tag contenha o título informado.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Atualização do Handler
- **Arquivo (`amb_cli/cli_modules/handlers_core/stitch_handler.py`):**
  - No bloco `sub == "generate"`:
    - Extrair `title = getattr(args, "title", None)`.
    - Repassar `title=title` para `client.generate_screen`.
    - Se `title` estiver preenchido e `output_file` não foi fornecido:
      - Criar slug limpo e definir caminho padrão: `output_file = f"./public/{slugify(title)}.html"`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_stitch_title_integration.py` cobrindo:
     - Repasse e incorporação do `title` durante a geração de tela.
     - Preservação do título na tag `<title>` do HTML gerado.
     - Auto-geração de caminho de saída amigável quando `title` é fornecido sem `--output`.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
