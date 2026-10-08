# 🎯 US-06: Engine Unificada de Personas e Validação de Templates (PersonaEngine e amb persona validate)

## 👤 User Story
> **Como** desenvolvedor configurando agentes no AMB_V2,  
> **Quero** uma `PersonaEngine` unificada com interpolação de variáveis dinâmicas e validação de seções mínimas via `amb persona validate`,  
> **Para que** todas as personas em `.amb/personas/` sigam a estrutura canônica necessária e recebam automaticamente o contexto arquitetural do repositório.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Descoberta e Fallbacks Centralizados**
  * **Dado** a classe `PersonaEngine` em `amb_cli/agents/persona_engine.py`;
  * **Quando** `load_persona(name: str)` for chamado;
  * **Então** deve buscar prioritariamente no diretório `.amb/personas/` do projeto;
  * **E** se a persona solicitada não existir como arquivo físico, deve recorrer aos fallbacks padrão de engenharia sem quebrar o fluxo.

* **Cenário 2: Interpolação Dinâmica de Variáveis**
  * **Dado** uma persona contendo placeholders como `{repo_name}`, `{stack}`, `{qa_command}`;
  * **Quando** for renderizada para envio ao agente;
  * **Então** a `PersonaEngine` deve interpolar esses valores a partir do contexto do projeto detectado em `amb_project.json`.

* **Cenário 3: Validação de Estrutura (amb persona validate)**
  * **Dado** o comando `amb persona validate`;
  * **Quando** for executado no terminal;
  * **Então** deve verificar todos os arquivos `.md` em `.amb/personas/`;
  * **E** deve validar a presença das seções essenciais: Título/Missão (`#`), Foco de Arquivos (`## Arquivos`) e Regras de Implementação (`## Regras`);
  * **E** deve emitir alerta colorido se alguma persona estiver fora do padrão recomendado.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. `amb_cli/agents/persona_engine.py` (Novo)
Implementar `PersonaEngine`:
- Descoberta e resolução de personas.
- Parser de seções markdown de personas.
- Interpolação de variáveis (`render_persona_template(content, context_vars)`).
- Método `validate_persona_file(filepath: str) -> List[str]` retornando lista de avisos/erros.

### 2. `amb_cli/cli_modules/handlers_core/persona_handler.py` (Novo)
Handler para o comando `amb persona validate`, listando o status de conformidade de cada persona.

### 3. `amb_cli/cli_modules/cli_parsers.py` e `amb_cli/cli_modules/cli_dispatch.py`
Registrar comando `amb persona` com subcomando `validate`.

### 4. `tests/test_persona_engine.py` (Novo)
Testes unitários cobrindo:
- Descoberta e carregamento de arquivos válidos e inválidos.
- Interpolação dinâmica de variáveis de contexto.
- Detecção de seções faltantes em arquivos malformados.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar testes unitários da PersonaEngine
pytest tests/test_persona_engine.py -v

# Validar suíte completa
pytest -q

# Testar validação de personas
python -m amb_cli.cli persona validate
```

---

## 📋 Definition of Done (DoD)
- [ ] `PersonaEngine` implementada com interpolação e fallbacks limpos.
- [ ] Subcomando `amb persona validate` operacional na CLI.
- [ ] Testes unitários dedicados em `tests/test_persona_engine.py` 100% passando.
- [ ] Arquivos novos com menos de 220 linhas cada.
