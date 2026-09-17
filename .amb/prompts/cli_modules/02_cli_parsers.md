# 🎯 Tarefa Jules: Auditoria e Otimização de `amb_cli/cli_modules/cli_parsers.py`

## 📌 Arquivo Alvo
- **Caminho:** `amb_cli/cli_modules/cli_parsers.py`
- **Estado Atual:** 310 linhas (Viola a Regra 02: teto de 300 linhas).
- **Responsabilidade Única (SRP - Regra 01):** Construir e retornar o `argparse.ArgumentParser` unificado da CLI com todos os subparsers e comandos registrados.

---

## 📐 Regras Arquiteturais Obrigatórias (`.agents/rules/`)
1. **Regra 01 (SRP):** Manter a função `create_parser()` estritamente focada na declaração dos argumentos e subparsers da CLI.
2. **Regra 02 (Atomização para IA):** O arquivo DEVE ter menos de 300 linhas (meta: ~240-270 linhas).
3. **Regra 03 (DRY & Imports Canônicos):** Imports limpos e canônicos (`from cli_modules.cli_handlers import ...`).
4. **Regra 04 (Tipagem Estrita):** Anotar a função com `create_parser() -> argparse.ArgumentParser`.
5. **Regra 05 (Documentação Concisa):** Docstring clara no topo do arquivo sem decorações excessivas.
6. **Regra 06 (Segurança Git & Testes):** Nenhuma alteração deve quebrar os comandos existentes da CLI ou os testes automatizados (`pytest` 100% verde).

---

## 🛠️ Itens Específicos a Verificar / Refatorar
1. **Preservação de 100% dos Comandos e Subparsers:**
   - Todos os 16 comandos principais devem continuar funcionando exatamente como configurados:
     `setup`, `prompt`, `check`, `config`, `monitor`, `advisor`, `gui`, `agent`, `jules`, `stitch`, `antigravity`, `validate`, `pipeline`, `schema`, `context`, `git`.
   - Todos os aliases (`init`, `status`, `settings`, `watch`, `sentinel`, `ask`, `ui`, `wizard`, `persona`) e subparsers de `jules`, `stitch`, `antigravity` e `git` devem ser preservados.
2. **Compactação Elegante:**
   - Eliminar quebras de linhas redundantes e agrupar helpers de registro ou dicionários de flags comuns para manter o código limpo, legível e bem abaixo de 300 linhas.
3. **Compatibilidade com `amb_cli/cli.py`:**
   - O ponto de entrada `from cli_modules.cli_parsers import create_parser` deve funcionar perfeitamente.

---

## 🧪 Validação Obrigatória
Antes de abrir o Pull Request:
```bash
python -m py_compile amb_cli/cli_modules/cli_parsers.py
python -m amb_cli --help
python -m amb_cli agent --help
python -m amb_cli jules --help
python -m pytest
```
Todos os testes unitários devem passar (100% green).

---

## 🚀 Ação Final Obrigatória: Abertura do Pull Request
Ao concluir todas as alterações e validar os testes com sucesso (100% green):
1. Você DEVE submeter/abrir o Pull Request no GitHub imediatamente.
2. Não encerre a sessão apenas no estado "Ready for submission"; confirme a criação do PR diretamente no GitHub com título e descrição claros das alterações.
