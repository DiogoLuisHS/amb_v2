# US-25: Suporte a Filtro AIP-160 em list_sources e amb jules sources --filter

## 📌 Contexto e Objetivo
A documentação da API REST do Google Jules (`https://jules.google/docs/api/reference/sources`) especifica que o endpoint `GET /v1alpha/sources` aceita uma expressão de filtro padronizada pelo Google API Improvement Proposal AIP-160:
```http
GET /v1alpha/sources?pageSize=50&filter=name%3Dsources%2Fgithub-myorg-myrepo
```
O parâmetro de consulta `filter` permite buscar fontes por nome, atributos de repositório ou branch (ex: `name=sources/source1 OR name=sources/source2`).

No AMB_V2, o método `JulesClient.list_sources()` aceita apenas `page_size`, e o comando `amb jules sources` não disponibiliza nenhuma flag para filtrar fontes diretamente na API. Para contas com múltiplas dezenas de repositórios conectados, isso exige listar todas as fontes e inspecioná-las manualmente.

Esta US implementa o suporte ao parâmetro `filter` em `JulesClient.list_sources`, na tool `run_list_sources`, e adiciona a flag `--filter` / `-f` no CLI `amb jules sources`.

---

## 📐 Requisitos Técnicos

### 1. Atualização do `JulesClient.list_sources`
- **Arquivo (`amb_cli/integrations/jules/jules_client.py`):**
  - Assinatura do método:
    ```python
    def list_sources(
        self,
        page_size: int = 50,
        filter_expr: Optional[str] = None
    ) -> List[Dict[str, Any]]:
    ```
  - Se `filter_expr` for fornecido e não vazio, incluir `"filter": filter_expr.strip()` no dicionário de `params` da requisição GET.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Atualização da Ferramenta `run_list_sources`
- **Arquivo (`amb_cli/integrations/jules/tools/list_sources.py`):**
  - Atualizar a assinatura da função:
    ```python
    def run_list_sources(
        as_json: bool = False,
        filter_expr: Optional[str] = None,
        client: Optional[JulesClient] = None
    ) -> List[Dict[str, Any]]:
    ```
  - Repassar `filter_expr=filter_expr` na invocação de `c.list_sources(...)`.
  - No `main()`, adicionar o argumento `--filter` (`-f`):
    ```python
    p.add_argument("--filter", "-f", help="Filtro AIP-160 para consultar fontes específicas na API.")
    ```

### 3. Integração na Camada CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `sources`:
    ```python
    j = _sc(js, "sources", "Lista fontes e repositórios conectados à conta Google Jules.", ["source"])
    j.add_argument("--filter", "-f", help="Filtro AIP-160 para consultar fontes específicas no Jules.")
    _j(j)
    ```
- **Arquivo (`amb_cli/cli_modules/handlers_core/jules_handler.py`):**
  - No bloco `elif sub in ["sources", "source"]:`:
    - Obter `filter_expr = getattr(args, "filter", None)`.
    - Passar `filter_expr=filter_expr` para `run_list_sources(...)`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_sources_filter.py` cobrindo:
     - Chamada a `JulesClient.list_sources(filter_expr=...)` repassando o parâmetro `filter` nos `params`.
     - Chamada a `JulesClient.list_sources()` sem filtro (sem chave `filter` nos `params`).
     - Execução de `run_list_sources(filter_expr="name=sources/github-org-repo")`.
     - Parsing correto da flag `--filter` no CLI parser de `amb jules sources`.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
