# 🎯 Tarefa Jules: Auditoria e Refatoração de `amb_cli/architecture/ai_context_builder.py`

## 📌 Arquivo Alvo
- **Caminho:** `amb_cli/architecture/ai_context_builder.py`
- **Estado Atual:** 384 linhas (Viola a Regra 02: teto de 300 linhas).
- **Responsabilidade Única (SRP - Regra 01):** Rastrear dependências de arquivos e gerar a ordem arquitetural de leitura para modelos de IA.

---

## 📐 Regras Arquiteturais Obrigatórias (`.agents/rules/`)
1. **Regra 01 (SRP):** Manter `AIContextBuilder` focado em seu papel de façade e orquestrador de contexto. Lógicas auxiliares densas (como mapeamento estático das 9 camadas ou tabelas de extensões) podem ser modularizadas em submódulo ou funções de suporte se necessário.
2. **Regra 02 (Atomização para IA):** O arquivo DEVE ter menos de 300 linhas (meta: ~220-250 linhas). Nenhum arquivo novo criado de suporte pode exceder 300 linhas.
3. **Regra 03 (DRY & Imports Canônicos):** Utilizar sempre imports canônicos absolutos (`from config.bootstrap import ensure_amb_env`, `from config import find_repo_root`). Proibido imports planos legados.
4. **Regra 04 (Tipagem Estrita):** 100% dos métodos públicos e funções auxiliares devem possuir type hints completos (`Set[str]`, `Dict[str, Any]`, `List[str]`, `Optional[str]`, `Tuple[str, bool]`).
5. **Regra 05 (Documentação Concisa):** Proibido banners gigantes decorativos ASCII. Cabeçalho declarativo limpo de 1 a 3 linhas.
6. **Regra 06 (Segurança Git & Testes):** Nenhuma alteração deve quebrar os testes unitários (`pytest` 100% verde).

---

## 🛠️ Itens Específicos a Verificar / Refatorar
1. **Preservação Integral da API Pública:**
   - O construtor `AIContextBuilder(root_dir: Path)` deve ser mantido.
   - Os métodos `scan_files()`, `analyze()`, `find_matching_nodes(query)`, `trace_module_chain(query)`, `classify_and_order_files(file_set, query)`, `_determine_file_layer(file)`, `generate_markdown(query, layers)` e a função `generate_context(target, output_json)` devem ser estritamente preservados com a mesma assinatura e comportamento, pois são consumidos por `amb_cli/agents/loop_core/cycle_dispatcher.py` e `tests/test_ai_context_builder.py`.
2. **Decomposição Elegante:**
   - Se decompor helpers para submódulo (ex: `amb_cli/architecture/context_core/`), certifique-se de expor aliases ou importar no namespace para total retrocompatibilidade.
3. **Limpeza e Type Hints:**
   - Assegurar type hints completos e tratamento defensivo de encoding UTF-8 ao ler arquivos.

---

## 🧪 Validação Obrigatória
Antes de abrir o Pull Request:
```bash
python -m py_compile amb_cli/architecture/ai_context_builder.py
python -m pytest tests/test_ai_context_builder.py
python -m pytest
```
Todos os testes unitários devem passar (100% green).

---

## 🚀 Ação Final Obrigatória: Abertura do Pull Request
Ao concluir todas as alterações e validar os testes com sucesso (100% green):
1. Você DEVE submeter/abrir o Pull Request no GitHub imediatamente.
2. Não encerre a sessão apenas no estado "Ready for submission"; confirme a criação do PR diretamente no GitHub com título e descrição claros das alterações.
