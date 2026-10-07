# 🎯 US-07: Expor Flag `--grounding` no Comando `amb context`

## 👤 User Story
> **Como** desenvolvedor utilizando a CLI do AMB_V2,  
> **Quero** poder executar `amb context --grounding`,  
> **Para que** eu possa solicitar a inclusão de diretrizes oficiais do Google Developer Knowledge diretamente pelo terminal.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Presença da flag `--grounding` no help da CLI**
  * **Dado** o comando de ajuda `amb context --help`;
  * **Quando** o parser exibir os argumentos disponíveis;
  * **Então** a flag `--grounding` deve estar documentada com a descrição de anexo de diretrizes oficiais.

* **Cenário 2: Propagação do argumento para o handler de contexto**
  * **Dado** que o usuário executou `amb context --grounding`;
  * **Quando** o handler `cmd_context` / `handle_cmd_context` for acionado;
  * **Então** deve extrair `args.grounding` e repassar `include_grounding=True` para o construtor de contexto.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. `amb_cli/cli_modules/cli_parsers.py`
Localize a seção do parser de `context` (aproximadamente linha 208):
```python
p = _c("context", "Gera o roteiro de leitura de arquivos por camadas para a IA.", cmd_context, ["ctx", "ai-context"])
p.add_argument("module", nargs="?", default="agenda", help="Nome do módulo ou pasta para rastrear (ex: agenda, kanban, projects).")
p.add_argument("--json", action="store_true", help="Retorna o resultado em JSON estruturado.")
# Adicione a flag:
p.add_argument("--grounding", action="store_true", help="Anexa diretrizes canônicas do Developer Knowledge ao roteiro.")
```
> ⚠️ **ATENÇÃO:** Mantenha a adição concisa em 1 linha para que `cli_parsers.py` continue abaixo de 270 linhas.

### 2. `amb_cli/cli_modules/handlers_core/context_handler.py` (ou onde `cmd_context` delega)
Repassar o argumento para o construtor:
```python
include_grounding = getattr(args, "grounding", False)
# Repassar include_grounding ao chamar o builder
```

---

## 🔍 Comandos de Verificação Local
```bash
# Validar help da CLI com a nova flag
python -m amb_cli.cli context --help

# Testar execução real com a flag
python -m amb_cli.cli context --grounding

# Validar conformidade de tamanho de cli_parsers.py (<= 300 linhas)
python -m amb_cli.cli validate amb_cli/cli_modules/cli_parsers.py
```

---

## 📋 Definition of Done (DoD)
- [ ] Argumento `--grounding` registrado no parser de `context`.
- [ ] Argumento repassado ao builder de contexto no handler de execução.
- [ ] `amb context --help` exibe a flag documentada.
- [ ] Arquivo `cli_parsers.py` mantido estritamente abaixo de 270 linhas.
- [ ] Suíte global `pytest` continua 100% verde.
