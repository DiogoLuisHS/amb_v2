# 🔒 Regra 06: Segurança em Git, Defensividade e Retrocompatibilidade

> **Escopo:** Controle de Versão, Operações Destrutivas e Estabilidade de APIs  
> **Objetivo:** Garantir integridade do repositório, preservação de histórico Git, proteção contra perda de dados e retrocompatibilidade estrita.

---

## 1. Preservação de Histórico Git (`git mv`)

- **Proibido Excluir e Recriar Arquivos:** Toda movimentação ou renomeação de arquivos deve ser executada obrigatoriamente via `git mv`.
- O Git deve rastrear 100% dos movimentos como renomeações limpas (`R100`), preservando a autoria, histórico de commits e rastreabilidade (`git blame`).
- Nunca versionar artefatos temporários, caches (`__pycache__`, `.pytest_cache`), credenciais (`.env`) ou diretórios de build (`*.egg-info`, `dist/`).

---

## 2. Garantia de Retrocompatibilidade (Zero Breaking Changes)

- **Shims de Compatibilidade:** Quando um módulo ou arquivo é realocado (como a migração de código para `amb_cli/`), um shim de compatibilidade leve deve ser mantido na localização original.
  - Exemplo: `cli.py` e `amb_bootstrap.py` na raiz redirecionam transparentemente para o novo pacote `amb_cli`.
- **Compatibilidade de Interfaces Públicas:** Assinaturas de métodos públicos, comandos e flags de CLI não devem ser removidos sem ciclo prévio de depreciação.

---

## 3. Operações Destrutivas com Guardrails Defensivos

- **Flag `--force` Obrigatória para Ações Críticas:**
  - Operações que alteram estado remoto, aprovam planos de execução ou encerram/excluem sessões devem implementar validações defensivas prévias.
  - Se a ação for forçada pelo usuário, deve ser exigida a flag explícita `--force` (ex: `amb jules approve <id> --force`).
- **Suporte a `--dry-run`:** Comandos de provisionamento, migração ou exclusão em lote devem disponibilizar simulação com `--dry-run`.

---

## 4. Testes Automatizados Sempre Verdes (100% Green)

- **Nenhum Commit com Testes Quebrados:** A suíte de testes unitários (`pytest`) deve rodar com 100% de sucesso antes de qualquer commit ou push.
- **Cobertura Contínua:** Novas funcionalidades, novos métodos de cliente e correções de bugs devem sempre ser acompanhados de seus respectivos testes unitários em `tests/`.
