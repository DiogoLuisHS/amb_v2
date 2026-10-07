# 🎯 US-08: Sincronização Completa de Documentações e Skills da CLI AMB

## 👤 User Story
> **Como** desenvolvedor e arquiteto de software utilizando o AMB_V2,  
> **Quero** documentações atualizadas e todas as 8 skills em `.agents/skills/` sincronizadas com as novas capacidades da CLI (`amb loop`, `amb hooks`, `amb stats`, `amb persona validate`, `amb validate --staged`),  
> **Para que** qualquer agente de IA ou desenvolvedor humano tenha referência canônica e cheatsheet preciso de todos os comandos do ecossistema.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Atualização do README Principal e Backlog MoSCoW**
  * **Dado** os arquivos `README.md` e `_docs/SUGGESTIONS.md`;
  * **Quando** forem revisados;
  * **Então** o `README.md` deve listar os novos comandos na tabela de referência da CLI (`amb loop`, `amb hooks`, `amb stats`, `amb persona validate`);
  * **E** o `_docs/SUGGESTIONS.md` deve marcar os itens implementados como concluídos com referência aos módulos criados.

* **Cenário 2: Sincronização de Skills Especializadas**
  * **Dado** o diretório `.agents/skills/`;
  * **Quando** inspecionado;
  * **Então** as skills abaixo devem refletir as novas capacidades:
    - `amb-master-ecosystem/SKILL.md`: Catálogo atualizado com os novos comandos.
    - `amb-autonomous-pipeline/SKILL.md`: Documentação de tolerância a falhas com `amb loop status/pause/resume` e `.amb/loop_state.json`.
    - `amb-antigravity-specialist/SKILL.md`: Documentação da `PersonaEngine` e validação com `amb persona validate`.
    - `amb-consumer-bootstrap/SKILL.md`: Instruções de pré-commit com `amb hooks install`.

* **Cenário 3: Atualização do CHANGELOG**
  * **Dado** o arquivo `_docs/CHANGELOG.md`;
  * **Quando** for atualizado;
  * **Então** deve registrar a nova versão com as melhorias de resiliência do loop, unificação do watcher, telemetria e hooks.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. `README.md`
Adicionar seções explicativas para:
- `amb loop status|pause|resume`
- `amb validate --staged` e `amb hooks install`
- `amb stats [--json]`
- `amb persona validate`

### 2. `_docs/SUGGESTIONS.md` e `_docs/CHANGELOG.md`
Atualizar matriz MoSCoW e notas de versão.

### 3. `.agents/skills/amb-master-ecosystem/SKILL.md` e skills irmãs
Incorporar comandos nas tabelas e seções de referência rápida.

### 4. `tests/test_cli_commands.py`
Adicionar testes garantindo que o parser da CLI responde a todos os novos comandos sem erro de sintaxe.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar help de todos os comandos novos
python -m amb_cli.cli loop --help
python -m amb_cli.cli hooks --help
python -m amb_cli.cli stats --help
python -m amb_cli.cli persona --help

# Validar suíte completa
pytest -q
```

---

## 📋 Definition of Done (DoD)
- [ ] README.md, CHANGELOG.md e SUGGESTIONS.md atualizados.
- [ ] Todas as 8 skills em `.agents/skills/` sincronizadas com as novas diretrizes.
- [ ] Testes de comandos CLI em `tests/test_cli_commands.py` 100% passando.
- [ ] Zero inconsistências entre documentação e código implementado.
