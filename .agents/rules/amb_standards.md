# 📐 Padrões e Diretrizes de Engenharia — AMB_V2 (Manifesto Mestre)

> **Versão:** 2.3.0 | **Status:** Ativo  
> Este documento é a fonte de autoridade central para desenvolvimento, refatoração e operação de agentes autônomos no ecossistema `amb_v2`. Ele consolida as regras atômicas residentes neste diretório.

---

## 🏛️ Princípios Arquiteturais Fundamentais

1. **Responsabilidade Única (SRP):**
   - Cada classe, módulo e função possui uma única razão para mudar.
   - Separação rígida entre parsers de linha de comando, handlers de apresentação, ferramentas de fachada e clientes de integração.
   - Detalhes completos: [`01_single_responsibility.md`](01_single_responsibility.md)

2. **Atomização de Arquivos e Otimização para IA:**
   - Granularidade de 100 a 250 linhas (teto de 300 linhas).
   - Proibição de God Files / God Classes.
   - Arquivos pequenos e autocontidos otimizam a atenção e o raciocínio de agentes como Google Jules e Gemini, reduzindo alucinações e consumo de tokens.
   - Detalhes completos: [`02_atomization_and_ai_context.md`](02_atomization_and_ai_context.md)

3. **Zero Redundância e Fonte Única da Verdade (DRY):**
   - Proibição estrita de duplicação de lógica, regex, URLs ou cálculos.
   - Todos os clientes Google herdam de `BaseGoogleClient` (retries, jitter, mascaramento de chaves, parsing).
   - Detalhes completos: [`03_dry_and_zero_redundancy.md`](03_dry_and_zero_redundancy.md)

4. **Qualidade de Código, Tipagem Estrita e Resiliência:**
   - Type Hints do Python obrigatórios em todas as assinaturas públicas.
   - Hierarquia de exceções derivada de `AmbError` com mensagens de resolução acionáveis.
   - Validação Fail-Fast (`require_env`) e suporte padrão a `--json`.
   - Detalhes completos: [`04_code_quality_and_typing.md`](04_code_quality_and_typing.md)

5. **Simplificação e Clareza de Comentários:**
   - Docstrings concisas (1 a 3 linhas) focadas no "o quê" e "por quê".
   - Eliminação de banners ASCII decorativos excessivos e comentários óbvios.
   - Comentários inline reservados unicamente para decisões não-triviais ou regras de negócio externas.
   - Detalhes completos: [`05_concise_documentation.md`](05_concise_documentation.md)

6. **Segurança em Git, Defensividade e Retrocompatibilidade:**
   - Movimentação obrigatória via `git mv` preservando 100% do histórico de commits.
   - Shims de compatibilidade mantidos na raiz (`cli.py`, `amb_bootstrap.py`) garantem zero breaking changes.
   - Guardrails e flags de proteção (`--force`, `--dry-run`) em operações destrutivas.
   - Suíte de testes automatizados com 100% de sucesso contínuo (`pytest`).
   - Detalhes completos: [`06_git_safety_and_compatibility.md`](06_git_safety_and_compatibility.md)

---

## 🚀 Execução e Validação de Conformidade

- Para listar todas as regras ativas no terminal:
  ```bash
  amb agy rules
  ```
- Para auditar um arquivo contra os padrões arquiteturais:
  ```bash
  amb validate <caminho_do_arquivo>
  ```
- Para rodar a suíte de testes de integridade:
  ```bash
  pytest
  ```
