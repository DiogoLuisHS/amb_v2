# 🎯 US-06: Integrar Grounding Semântico em `AIContextBuilder`

## 👤 User Story
> **Como** agente autônomo consumindo o blueprint de arquivos do AMB,  
> **Quero** que o método `build_context` em `ai_context_builder.py` aceite o parâmetro `include_grounding: bool = False`,  
> **Para que** as diretrizes oficiais de tecnologia possam ser anexadas ao blueprint sob demanda sem estourar o limite de linhas do arquivo.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Blueprint com grounding habilitado (`include_grounding=True`)**
  * **Dado** uma instância de `AIContextBuilder`;
  * **Quando** `build_context(..., include_grounding=True)` for chamado;
  * **Então** deve detectar as tecnologias configuradas no projeto e anexar o bloco gerado por `DeveloperKnowledgeGrounder().render_markdown(...)` ao final do blueprint.

* **Cenário 2: Blueprint sem grounding (`include_grounding=False`)**
  * **Dado** uma chamada padrão `build_context(...)` sem especificar `include_grounding`;
  * **Quando** o roteiro for montado;
  * **Então** a seção de diretrizes NÃO deve ser anexada, mantendo o formato clássico.

* **Cenário 3: Respeito rigoroso ao limite de 300 linhas**
  * **Dado** que `amb_cli/architecture/ai_context_builder.py` possui 280 linhas;
  * **Quando** a integração for adicionada;
  * **Então** a modificação deve ter no máximo 6 linhas;
  * **E** o arquivo não deve ultrapassar 288 linhas.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### `amb_cli/architecture/ai_context_builder.py`
> ⚠️ **ATENÇÃO À REGRA DE 300 LINHAS:** `ai_context_builder.py` está com 280 linhas. Não escreva formatações manuais ou loops extensos dentro deste arquivo.

1. Atualize a assinatura do método principal (ex: `build_context` ou `generate_roadmap`) para aceitar o parâmetro opcional:
   ```python
   include_grounding: bool = False
   ```
2. No ponto final onde a lista de linhas/blocos do Markdown é consolidada, adicione apenas a delegação enxuta:
   ```python
   if include_grounding:
       from architecture.context_core.knowledge_grounding import DeveloperKnowledgeGrounder
       detected_stacks = list(self.project_config.get("stack", {}).keys()) if hasattr(self, "project_config") else []
       grounding_block = DeveloperKnowledgeGrounder().render_markdown(detected_stacks)
       if grounding_block:
           output_lines.append(grounding_block)
   ```

---

## 🔍 Comandos de Verificação Local
```bash
# Validar contagem de linhas do arquivo
python -c "p = 'amb_cli/architecture/ai_context_builder.py'; lines = len(open(p, encoding='utf-8').readlines()); print('Total de linhas:', lines); assert lines < 290, 'Estourou limite!'"

# Executar suíte de testes de ai_context_builder
pytest tests/test_ai_context_builder.py -v

# Validar conformidade arquitetural
python -m amb_cli.cli validate amb_cli/architecture/ai_context_builder.py
```

---

## 📋 Definition of Done (DoD)
- [ ] Parâmetro opcional `include_grounding: bool = False` adicionado na assinatura do builder.
- [ ] Delegação de 1 linha para `DeveloperKnowledgeGrounder().render_markdown(...)`.
- [ ] Arquivo `ai_context_builder.py` mantido rigorosamente abaixo de 290 linhas.
- [ ] Testes existentes em `tests/test_ai_context_builder.py` continuam passando com 100% de sucesso.
