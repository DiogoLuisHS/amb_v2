# US-13: Extração de Código e Recuperação de Sessões do Jules (amb jules extract)

## 📌 Contexto e Objetivo
Quando uma sessão do Jules é concluída sem a criação de um Pull Request no GitHub (por exemplo, quando o Jules não tem permissão para criar PRs, em sessões manuais ou falhas de publicação), as modificações geradas continuam preservadas no payload da sessão (`changeSet.gitPatch.unidiffPatch`).
Esta funcionalidade introduz o comando `amb jules extract <session_id>` para extrair o código/patch da sessão e salvar em arquivo `.patch` ou aplicá-lo diretamente no repositório de trabalho local via `git apply`, garantindo zero perda de código.

---

## 📐 Requisitos Técnicos

1. **Módulo Extrator de Sessões (`amb_cli/integrations/jules/jules_core/session_extractor.py`):**
   - Criar a classe `SessionExtractor`:
     - Método estático `extract_patch(session_data: dict) -> str`:
       - Percorre `outputs` da sessão buscando `changeSet.gitPatch.unidiffPatch`.
       - Se não houver patch, levanta `AmbError` com mensagem amigável e dica de resolução.
     - Método estático `save_patch(patch_content: str, dest_path: Path) -> Path`:
       - Cria os diretórios pais se não existirem.
       - Salva o arquivo com `encoding="utf-8", errors="replace"`.
     - Método estático `apply_patch(patch_content: str, repo_root: Path) -> tuple[bool, str]`:
       - Aplica o patch usando o comando `git apply` no repositório.
       - Retorna `(success: bool, message: str)`.

2. **Parser e Handler na CLI (`cli_parsers.py` e `jules_handler.py`):**
   - No subparser do `amb jules`, adicionar comando `extract`:
     - Argumento obrigatório: `session_id` (ID da sessão do Jules).
     - `--dest`, `-d`: Caminho de destino para salvar o patch (Padrão: `.amb/patches/session_<session_id>.patch`).
     - `--apply`, `-a`: Flag booleana que, além de extrair, aplica as alterações no workspace atual via `git apply`.
   - No `jules_handler.py`, implementar a ação conectando com `JulesClient.get_session` e `SessionExtractor`.

3. **Formatação e Feedback Visual:**
   - Mensagem de sucesso indicando onde o patch foi salvo e a quantidade de linhas do patch.
   - Se `--apply` for passado, informar se a aplicação do patch no Git foi bem-sucedida.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes:** Criar `tests/test_session_extractor.py` cobrindo:
   - Extração de patch a partir de payload mockado da sessão.
   - Tratamento de erro quando a sessão não contém `unidiffPatch`.
   - Salvamento do patch em arquivo.
   - Aplicação de patch mockando chamada ao Git.
   - Teste de invocação via CLI (`amb jules extract <id>`).
2. **Qualidade de Código:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Todos os arquivos estritamente abaixo do limite de 300 linhas (Regra 02).
   - Tipagem estrita com `typing` e exceções `AmbError` (Regra 04).
   - Zero dependências externas novas.
